import simplejson
from pylab import *

from rdatkit.datahandlers import RDATFile, RDATSection, ISATABFile

from src.models import *


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

            row_limits.append({'y_min':0, 'y_max':max(peaks_row) + 0.5, 'x_min':min(seqpos), 'x_max':max(seqpos)})

            if data.errors.strip():
                errors_row = array([float(x) for x in data.errors.split(',')])
                errors_row[isnan(errors_row)] = 0
                errors_row[isinf(errors_row)] = 0
            else:
                errors_row = [0.] * len(seqpos)

            for j in range(len(peaks_row)):
                if entry.type == "SS" and is_eterna:
                    if annotations.has_key("sequence"):
                        if len(annotations["sequence"][0]) <= j:
                            seq = 'X'
                        else:
                            seq = annotations["sequence"][0][j]
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
                    data_matrix.append({'x':i, 'y':j, 'val':round(peaks_row[j], 3), 'err':round(errors_row[j], 3), 'seq':seq, 'mut':mut_flag})
                else:
                    data_matrix.append({'x':i, 'y':j, 'val':round(peaks_row[j], 3), 'err':round(errors_row[j], 3), 'seq':seq})
                data_mean.append(peaks_row[j])

        precalc_structures = precalc_structures.strip(',') + ']'
        data_mean = array(data_mean)
        data_sd = std(data_mean)
        data_mean = mean(data_mean)

        json = {'data':data_matrix, 'peak_max':data_max, 'peak_min':round(data_min, 3), 'peak_mean':round(data_mean, 3), 'peak_sd':round(data_sd, 3), 'row_lim':row_limits, 'x_labels':x_labels, 'y_labels':y_labels, 'precalc_structures':precalc_structures}
        open(PATH.DATA_DIR['RDAT_FILE_DIR'] + '/' + entry.rmdb_id + '/data_heatmap.json', 'w').write(simplejson.dumps(json, sort_keys=True, indent=' ' * 4))
    except ConstructSection.DoesNotExist:
        return None


def save_json_tags(entry):
    rdat_ver = open(PATH.DATA_DIR['RDAT_FILE_DIR'] + '/' + entry.rmdb_id + '/' + entry.rmdb_id + '.rdat', 'r').readline().strip().split('\t')[-1]

    tags_basic = {'rmdb_id':entry.rmdb_id, 'comments':entry.comments, 'version':entry.version, 'construct_count':entry.construct_count, 'data_count':entry.data_count,  'status':entry.status, 'type':entry.type, 'pdb_ids':entry.pdb_ids, 'description':entry.description, 'pubmed_id':entry.publication.pubmed_id, 'pub_title':entry.publication.title, 'authors':entry.publication.authors, 'rdat_ver':rdat_ver, 'creation_date':entry.creation_date.strftime('%x'), 'owner_name':entry.owner.first_name+' '+entry.owner.last_name,'owner':entry.owner.username, 'latest':entry.supercede_by}
    tags_annotation = {'annotation':entry.annotations}

    c = ConstructSection.objects.get(entry=entry)
    c.datas = DataSection.objects.filter(construct_section=c).order_by('id')
    tags_data_annotation = {}
    for i,d in enumerate(c.datas):
        d.annotations = trim_combine_annotation(DataAnnotation.objects.filter(section=d).order_by('name'))
        tags_data_annotation[i] = d.annotations
    tags_annotation['data_annotation'] = tags_data_annotation

    c.err_ncol = c.datas[0].errors.split(',')
    if len(c.err_ncol) == 1 and (not len(c.err_ncol[0])): 
        c.err_ncol = 0
    else:
        c.err_ncol = len(c.err_ncol)
    xsel_str = c.xsel.split(',')
    if len(xsel_str):
        c.xsel_len = len(c.xsel)
    else:
        c.xsel_len = 0
    seqpos_str = c.seqpos.split(',')
    if (int(seqpos_str[-1]) - int(seqpos_str[0]) + 1 != len(seqpos_str)):
        c.seqpos = '</code>,</span> <span style="display:inline-block; width:75px;"><code>'.join(seqpos_str)
        c.seqpos = '<span style="display:inline-block; width:75px;"><code>' + c.seqpos + '</code></span>'
    else:
        c.seqpos = '<code>' + seqpos_str[0] + '</code><b>:</b><code>' + seqpos_str[-1] + '</code>'
    c.seqpos_len = len(seqpos_str)

    tags_construct = {'sequence':c.sequence, 'structure':c.structure, 'offset':c.offset, 'sequence_len':len(c.sequence), 'structure_len':len(c.structure), 'data_nrow':len(c.datas), 'data_ncol':len(c.datas[0].values.split(',')), 'err_ncol':c.err_ncol, 'xsel_len':c.xsel_len, 'seqpos_len':c.seqpos_len, 'seqpos':c.seqpos, 'name':c.name}

    tags_all = dict(tags_basic.items() + tags_construct.items() + tags_annotation.items())
    open(PATH.DATA_DIR['RDAT_FILE_DIR'] + '/' + entry.rmdb_id + '/data_tags.json', 'w').write(simplejson.dumps(tags_all, sort_keys=True, indent=' ' * 4))


def save_json(rmdb_id):
    entry = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version')[0]

    if (entry.pdb is not None) and len(entry.pdb.strip()) > 0:
        entry.pdb_ids = [x.strip() for x in entry.pdb.split(',')]
    else:
        entry.pdb_ids = []
    entry.annotations = trim_combine_annotation(EntryAnnotation.objects.filter(section=entry))

    save_json_tags(entry)
    save_json_heatmap(entry)


def review_entry(new_stat, rmdb_id, cid):
    construct = ConstructSection.objects.get(id=cid)
    entry = RMDBEntry.objects.filter(id=construct.entry.id).order_by('-version')[0]
    if new_stat == "PUB":
        rdatfile = RDATFile()
        file_name = '%s%s/%s_%s.rdat' % (PATH.DATA_DIR['RDAT_FILE_DIR'], rmdb_id, rmdb_id, entry.version)
        if not os.path.isfile(file_name):
            file_name = '%s%s/%s.rdat' % (PATH.DATA_DIR['RDAT_FILE_DIR'], rmdb_id, rmdb_id)
        rf = open(file_name, 'r')
        rdatfile.load(rf)
        rf.close()
        # for k in rdatfile.constructs:
        #     c = rdatfile.constructs[k]
        #     entry.has_traces = generate_images(construct, c, entry.type, engine='matplotlib')

        # generate_varna_thumbnails(entry)
        save_json(entry.rmdb_id)

    entry.status = new_stat
    entry.save()
