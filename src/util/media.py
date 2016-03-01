import glob
import matplotlib
from pylab import *
import simplejson
import subprocess

from rdatkit.view import VARNA

from src.models import *
from src.settings import *
from src.util.util import get_entry_version

matplotlib.use('Agg')


def trim_combine_annotation(annotations):
    a_trimmed = {}
    for a in annotations:
        if (a.name not in a_trimmed):
            a_trimmed[a.name] = [a.value]
        else:
            a_trimmed[a.name].append(a.value)
    if a_trimmed.has_key("experimentType"):
        a_trimmed.pop("experimentType")
    return a_trimmed


def save_json_heatmap(entry):
    (maxlen, maxlen_flag) = (256, False)

    construct = ConstructSection.objects.get(entry=entry)
    construct.datas = DataSection.objects.filter(construct_section=construct).order_by('id')
    construct.data_count = range(len(construct.datas))
    if len(construct.datas) > maxlen:
        maxlen_flag = True
    for d in construct.datas:
        d.annotations = trim_combine_annotation(DataAnnotation.objects.filter(section=d).order_by('name'))

    precalc_structures = '['
    accepted_tags = ['modifier', 'chemical', 'mutation', 'structure', 'lig_pos', 'MAPseq', 'EteRNA']
    try:
        datas = construct.datas
        seqpos = [int(x) for x in construct.seqpos.strip('][').split(',')]
        offset = construct.offset
        sequence = construct.sequence

        x_labels = ['%s%s' % (sequence[x - 1 - offset], x) for x in seqpos]
        y_labels = []
        row_limits = []
        (data_matrix, data_max, data_min, data_mean, data_sd) = ([], 0., 0., [], 0.)

        for i, data in enumerate(datas):
            annotations = data.annotations
            if 'structure' in annotations:
                precalc_structures += '"%s",' % annotations['structure']
                del(annotations['structure'])
            else:
                precalc_structures += '"%s",' % data.structure

            is_eterna = ("EteRNA" in construct.name) or ("Eterna" in construct.name) or ("EteRNA" in annotations) or ("EteRNA" in annotations)
            if entry.type == 'MM':
                if 'mutation' in annotations:
                    field = 'mutation'
                elif 'chemical' in annotations:
                    field = 'chemical'
                elif 'partner' in annotations:
                    field = 'partner'
                else:
                    field = ''
                if field:
                    y_label_tmp = annotations[field][0]
                else:
                    annotations_flatten = [y for x in annotations.values() for y in x]
                    y_label_tmp = '%s' % (','.join(annotations_flatten))
            elif entry.type == "MA":
                if annotations.has_key("lig_pos"):
                    y_label_tmp = 'lig_pos:%s' % annotations["lig_pos"][0]
                if annotations.has_key("ligpos"):
                    y_label_tmp = 'lig_pos:%s' % annotations["ligpos"][0]
            elif entry.type == "SS" and is_eterna:
                if annotations:
                    if annotations.has_key("MAPseq"):
                        y_label_tmp = annotations["MAPseq"]
                        for j in range(len(y_label_tmp)):
                            if y_label_tmp[j].find("ID:") == 0:
                                y_label_tmp = y_label_tmp[j]
                                break
                    else:
                        y_label_tmp = annotations["EteRNA"]
                        for j in range(len(y_label_tmp)):
                            if y_label_tmp[j].find("ID:") == 0:
                                y_label_tmp = y_label_tmp[j]
                                break

                else:
                    y_label_tmp = "Error_in_row"
            else:
                annotations_flatten = [y for x in annotations.values() for y in x]
                y_label_tmp = '%s' % (','.join(annotations_flatten))
            y_labels.append(y_label_tmp)
            
            peaks_row = array([float(x) for x in data.values.split(',')])
            peaks_row[isnan(peaks_row)] = 0
            peaks_row[isinf(peaks_row)] = 0
            data_max = max(max(peaks_row), data_max)
            data_min = max(min(peaks_row), data_min)

            row_limits.append({'y_min': 0, 'y_max': max(peaks_row) + 0.5, 'x_min': min(seqpos), 'x_max': max(seqpos)})

            if data.errors.strip():
                errors_row = array([float(x) for x in data.errors.split(',')])
                errors_row[isnan(errors_row)] = 0
                errors_row[isinf(errors_row)] = 0
            else:
                errors_row = [0.] * len(seqpos)

            for j in range(len(peaks_row)):
                if entry.type == "SS" and is_eterna:
                    if annotations.has_key("sequence"):
                        seq = 'X' if (len(annotations["sequence"][0]) <= j) else annotations["sequence"][0][j]
                    else:
                        print "ERROR parsing annotation row:", i+1, ": ", annotations
                        seq = 'X'   
                else:
                    seq = sequence[j]
                mut_flag = 0

                if 'mutation' in annotations:
                    mutpos = annotations['mutation']
                    for mut in mutpos:
                        mut = mut.strip()
                        if ':' in mut:
                            if "(" in mut and ")" in mut:
                                mut_start = int(mut[mut.find('(')+1 : mut.find(':')])
                                mut_end = int(mut[mut.find(':')+1 : mut.find(')')])
                                if (j + offset + 1) >= mut_start and (j + offset + 1) <= mut_end:
                                    idx = j+offset+1-mut_start
                                    muts = mut[mut.find(')')+1:]
                                    seq= muts[idx]
                                    mut_flag = 1
                            else:
                                muts = mut.split(":")
                                for mut_split in muts:
                                    if seq == mut_split[0] and int(mut_split[1:-1]) == (j + offset + 1):
                                        seq = mut_split[-1]
                                        mut_flag = 1
                        else:
                            if seq == mut[0] and int(mut[1:-1]) == (j + offset + 1):
                                seq = mut[-1]
                                mut_flag = 1

                if mut_flag:
                    data_matrix.append({'x': i, 'y': j, 'val': round(peaks_row[j], 3), 'err': round(errors_row[j], 3), 'seq': seq, 'mut': mut_flag})
                else:
                    data_matrix.append({'x': i, 'y': j, 'val': round(peaks_row[j], 3), 'err': round(errors_row[j], 3), 'seq': seq})
                data_mean.append(peaks_row[j])

        precalc_structures = precalc_structures.strip(',') + ']'
        data_mean = array(data_mean)
        data_sd = std(data_mean)
        data_mean = mean(data_mean)

        json = {'data': data_matrix, 'peak_max': data_max, 'peak_min': round(data_min, 3), 'peak_mean': round(data_mean, 3), 'peak_sd': round(data_sd, 3), 'row_lim': row_limits, 'x_labels': x_labels, 'y_labels': y_labels, 'precalc_structures': precalc_structures}
        open('%s/%s-hmap.json' % (PATH.DATA_DIR['JSON_DIR'], entry.rmdb_id), 'w').write(simplejson.dumps(json, sort_keys=True, indent=' ' * 4))
    except ConstructSection.DoesNotExist:
        return None


def save_json_tags(entry):
    rdat_ver = open('%s/%s/%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], entry.rmdb_id, entry.rmdb_id), 'r').readline().strip().split('\t')[-1]
    if (entry.pdb is not None) and len(entry.pdb.strip()) > 0:
        entry.pdb_ids = [x.strip() for x in entry.pdb.split(',')]
    else:
        entry.pdb_ids = []
    entry.annotations = trim_combine_annotation(EntryAnnotation.objects.filter(section=entry))
    ver_list = get_entry_version(entry.rmdb_id)

    tags_basic = {'rmdb_id': entry.rmdb_id, 'comments': entry.comments, 'version': entry.version, 'versions': ver_list, 'construct_count': entry.construct_count, 'data_count': entry.data_count,  'status': entry.status, 'type': entry.type, 'pdb_ids': entry.pdb_ids, 'description': entry.description, 'pubmed_id': entry.publication.pubmed_id, 'pub_title': entry.publication.title, 'authors': entry.publication.authors, 'rdat_ver': rdat_ver, 'creation_date': entry.creation_date.strftime('%x'), 'owner_name': entry.owner.first_name+' '+entry.owner.last_name,'owner': entry.owner.username, 'latest': entry.supercede_by}
    tags_annotation = {'annotation': entry.annotations}

    c = ConstructSection.objects.get(entry=entry)
    c.datas = DataSection.objects.filter(construct_section=c).order_by('id')
    tags_data_annotation = {}
    for i, d in enumerate(c.datas):
        d.annotations = trim_combine_annotation(DataAnnotation.objects.filter(section=d).order_by('name'))
        tags_data_annotation[i] = d.annotations
    tags_annotation['data_annotation'] = tags_data_annotation

    c.err_ncol = c.datas[0].errors.split(',')
    c.err_ncol = 0 if (len(c.err_ncol) == 1 and (not len(c.err_ncol[0]))) else len(c.err_ncol)
    xsel_str = c.xsel.split(',')
    c.xsel_len = len(c.xsel) if len(xsel_str) else 0
    seqpos_str = c.seqpos.split(',')
    if (int(seqpos_str[-1]) - int(seqpos_str[0]) + 1 != len(seqpos_str)):
        c.seqpos = '</code>,</span> <span style="display:inline-block; width:75px;"><code>'.join(seqpos_str)
        c.seqpos = '<span style="display:inline-block; width:75px;"><code>' + c.seqpos + '</code></span>'
    else:
        c.seqpos = '<code>' + seqpos_str[0] + '</code><b>:</b><code>' + seqpos_str[-1] + '</code>'
    c.seqpos_len = len(seqpos_str)

    tags_construct = {'sequence': c.sequence, 'structure': c.structure, 'offset': c.offset, 'sequence_len': len(c.sequence), 'structure_len': len(c.structure), 'data_nrow': len(c.datas), 'data_ncol': len(c.datas[0].values.split(',')), 'err_ncol': c.err_ncol, 'xsel_len': c.xsel_len, 'seqpos_len': c.seqpos_len, 'seqpos': c.seqpos, 'name': c.name}

    tags_all = dict(tags_basic.items() + tags_construct.items() + tags_annotation.items())
    open('%s/%s-tags.json' % (PATH.DATA_DIR['JSON_DIR'], entry.rmdb_id), 'w').write(simplejson.dumps(tags_all, sort_keys=True, indent=' ' * 4))


def save_json(rmdb_id):
    entry = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version')[0]
    save_json_tags(entry)
    save_json_heatmap(entry)


def get_arrays(datas):
    (values, traces, reads, xsels, errors) = ([], [], [], [], [])

    for d in datas:
        values.append(d.values)
        traces.append(d.trace)
        reads.append(d.reads)
        xsels.append(d.xsel)
        errors.append(d.errors)
    return (array(values), array(traces), array(reads), array(xsels), array(errors))


def correct_rx_bonus(data, construct):
    vals = [float(x) for x in data.values.split(',')]
    seqpos = [int(x) - construct.offset - 1 for x in construct.seqpos.strip('[]').split(',')]
    bonuses = [-0.1] * len(construct.sequence)
    val_mean = sum(vals) / len(vals)
    for i, s in enumerate(seqpos):
        if vals[i] < -0.01:
            bonuses[s] = val_mean
        else:
            bonuses[s] = vals[i]
    return bonuses


def save_thumb(entry):
    try:
        c = ConstructSection.objects.get(entry=entry)
        datas = DataSection.objects.filter(construct_section=c)
        file_name = '%s%s' % (PATH.DATA_DIR['THUMB_DIR'], entry.rmdb_id)

        is_eterna = 'ETERNA' in entry.rmdb_id
        is_structure = (c.structure) and ('(' in c.structure)
        is_large = len(datas) > 100
        is_SS = entry.type in ('SS', 'TT')

        if is_structure and is_SS and (not is_large) and (not is_eterna):
            height = 200
            for i, data in enumerate(datas[:min(6, len(datas))]):
                bonuses = correct_rx_bonus(data, c)
                cms = VARNA.get_colorMapStyle(bonuses)

                VARNA.cmd('\" \"', c.structure, '%s-%s.png' % (file_name, i), options={'colorMapStyle': cms, 'colorMap': bonuses, 'bpStyle': 'simple', 'baseInner': '#FFFFFF', 'periodNum': 400, 'spaceBetweenBases': 0.6, 'flat': False} )
                subprocess.check_call('optipng %s-%s.png' % (file_name, i), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            subprocess.check_call('convert -delay 100 -resize 300x300 -background none -gravity center -extent 300x300 -loop 0 %s-*.png %s.gif' % (file_name, file_name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            subprocess.check_call('convert %s%s-rx.png %s.gif' % (PATH.DATA_DIR['IMG_DIR'], entry.rmdb_id, file_name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if (not entry.data_count): entry.data_count = len(datas[0].values.split(','))
            height = 200 * pow(len(datas), 2) / entry.data_count

            if (len(datas) < 3): height = len(datas) * 10
            height = min(height, 1000)
            if not is_eterna: height = min(height, 250)

        width = 200
        subprocess.check_call('mogrify -format gif -thumbnail %sx%s! %s.gif' % (width, height, file_name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        tmp_file = glob.glob('%s-*.png' % file_name)
        for f in tmp_file:
            os.remove(f)
    except ConstructSection.DoesNotExist:
        print 'FATAL! There are no constructs for entry %s' % entry.rmdb_id


def save_image(rmdb_id, construct_model, construct_section, entry_type):
    data = DataSection.objects.filter(construct_section=construct_model)
    (values, traces, reads, xsels, errors) = ([], [], [], [], [])
    for d in data:
        values.append([float(x) for x in d.values.strip().split(',')])
        if d.trace:
            traces.append([float(x) for x in d.trace.strip().split(',')])
        if d.reads:
            reads.append([float(x) for x in d.reads.strip().split(',')])
        if d.errors:
            errors.append([float(x) for x in d.errors.strip().split(',')])
        if d.xsel:
            xsels.append([float(x) for x in d.xsel.strip().split(',')])
    (values_array, trace_array, reads_array, xsel_array, errors_array) = get_arrays(construct_section.data)
    
    file_name = '%s/%s' % (PATH.DATA_DIR['IMG_DIR'], rmdb_id)
    (values_dims, trace_dims, values_mean, values_std) = (shape(values_array), shape(trace_array), values_array.mean(axis=-1), values_array.std(axis=0))

    if entry_type == 'MM':
        order = []
        order_offset = 0
        for i, data in enumerate(construct_section.data):
            if 'mutation' in data.annotations:
                if data.annotations['mutation'][0].upper() == 'WT':
                    order.append(order_offset)
                    order_offset += 1
                else:
                    i_order = data.annotations['mutation'][0].replace('Lib1-', '').replace('Lib2-', '').replace('Bad Quality', '').replace('badQuality', '').replace('warning:', '').replace(',', '').strip()
                    order.append(int(i_order[1:-1]))
            else:
                order.append(i)
        order = [i[0] for i in sorted(enumerate(order), key=lambda x:x[1])] #[::-1]
    else:
        order = range(values_dims[0])
    # if entry_type != 'MA':
        # order = order[::-1]
    

    figure(1)
    frame = gca()
    frame.axes.get_xaxis().set_visible(False)
    frame.axes.get_yaxis().set_visible(False)

    is_trace = (size(trace_array) > 0) or (size(reads_array) > 0)
    if size(trace_array) > 0:
        aspect_ratio = shape(trace_array[order, :])[1] / float(shape(trace_array)[0]) if (entry_type == 'MM') else 'auto'
        imshow(trace_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=trace_array.mean() + 0.4 * trace_array.std(), aspect=aspect_ratio, interpolation='nearest')
    if size(reads_array) > 0:
        aspect_ratio = shape(reads_array[order, :])[1] / float(shape(reads_array)[0]) if (entry_type == 'MM') else 'auto'
        imshow(reads_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=reads_array.mean() + 0.4 * reads_array.std(), aspect=aspect_ratio, interpolation='nearest')

    if is_trace:
        savefig(file_name + '-tr.png', bbox_inches='tight')
        subprocess.check_call('optipng %s%s-tr.png' % (PATH.DATA_DIR['IMG_DIR'], rmdb_id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    is_eterna = 'ETERNA' in construct_model.entry.rmdb_id
    aspect_ratio = 'auto' if (is_eterna or shape(values_array)[0] < 3) else 'equal'
    if entry_type == "MA":
        sub_id = tril_indices(min(shape(values_array)))
        if (values_array[sub_id].mean() > 10):
            outliers = where(values_array > values_array[sub_id].mean() * 3)
            values_array[outliers] = values_array[sub_id].mean() * 3
        vmax_adjust = values_array[sub_id].mean() * 2 #+ values_array[sub_id].std()*0.35
    else:
        vmax_adjust = values_array.mean() * 1.5 #+ values_array.std()*0.35
    vmax_adjust = max(0, values_array.mean() + values_array.std() * 0.5)

    figure(2)
    clf()
    imshow(values_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=vmax_adjust, aspect=aspect_ratio, interpolation='nearest')
    frame = gca()
    frame.axes.get_xaxis().set_visible(False)
    frame.axes.get_yaxis().set_visible(False)
    savefig(file_name + '-rx.png', bbox_inches='tight')
    subprocess.check_call('optipng %s%s-rx.png' % (PATH.DATA_DIR['IMG_DIR'], rmdb_id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # figure(3)
    # clf()
    # tight_layout()
    # if is_eterna:
    #     aspect_ratio = .025 #shape(values_array)[0]/shape(values_array)[1] / 5
    #     dpi = 600
    # else:
    #     aspect_ratio = 'equal'
    #     dpi = 120
    # imshow(values_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=vmax_adjust, aspect=aspect_ratio, interpolation='nearest')
    # frame = gca()
    # frame.axes.get_xaxis().set_visible(False)
    # frame.axes.get_yaxis().set_visible(False)
    # savefig(dir+'/reactivity_equal.png', bbox_inches='tight', pad_inches=1e-2, dpi=dpi)
    close('all')

    return is_trace

