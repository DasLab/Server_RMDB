
from rdatkit.datahandlers import RDATFile
from rdatkit import rna, secondary_structure, mapping, view

from src.models import *
from src.settings import *

from numpy import *


def parse_rdat_data(request, is_get_file):
    sequences, titles, structures, modifiers, messages, valerrors, offset_seqpos = ([],[],[],[],[],[],[])
    temperature = 37
    rdatfile = RDATFile()
    refstruct = secondary_structure.SecondaryStructure()

    if len(request.POST['sequences']):
        messages.append('WARNING: Using sequences and/or structures from received RDAT file content. Original input in fields were overwritten.')

    if is_get_file:
        uploadfile = request.FILES['rdatfile']
        rf = write_temp_file('/tmp/%s'%uploadfile.name)
    else:
        rmdbid = request.POST['rmdbid'].strip()
        version = RMDBEntry.get_current_version(rmdbid)
        rf = open(PATH.DATA_DIR['FILE_DIR'] + '/%s/%s_%s.rdat' % (rmdbid, rmdbid, version), 'r')
    rdatfile.load(rf)
    rf.close()

    is_modified = 'modifier' in rdatfile.annotations
    if is_modified:
        modifier = ','.join(rdatfile.annotations['modifier'])

    for cname in rdatfile.constructs:
        c = rdatfile.constructs[cname]

        if 'temperature' in c.annotations:
            temperature = c.annotations['temperature']

        seq = ''
        bonuses_1d = []
        bonuses_2d = []
        seqpos_min = min(c.seqpos)

        if ('clipsequence' in request.POST):
            if len(c.sequence) >= max(c.seqpos) - c.offset - 1:
                seq_clipped = ''.join([c.sequence[i - c.offset - 1] for i in sorted(c.seqpos)])
            else: 
                messages.append('WARNING: SEQUENCE and SEQPOS mismatch for construct %s in RDAT file. SEQPOS ignored.' % c.name)
                c.seqpos = [(i + 1) for i in range(len(c.sequence))]
                seq_clipped = c.sequence

            if len(c.structure) >= max(c.seqpos) - c.offset - 1:
                struct_clipped = ''.join([c.structure[i - c.offset - 1] for i in sorted(c.seqpos)])
            else:
                messages.append('WARNING: STRUCTURE and SEQPOS mismatch for construct %s in RDAT file. STRUCTURE ignored.' % c.name)
                struct_clipped = '.'*(max(c.seqpos) - c.offset - 1)
                c.structure = struct_clipped

            seq = seq_clipped
            struct = struct_clipped
        else:
            seq = c.sequence
            struct = c.structure

        if len(refstruct) == 0:
            refstruct = secondary_structure.SecondaryStructure(dbn=struct)

        for d in c.data:
            if is_modified or ('modifier' in d.annotations):
                s = seq
                is_2d = False
                if ('mutation' in d.annotations):
                    for mut in d.annotations['mutation']:
                        if 'WT' == mut.strip():
                            break
                        is_2d = True
                        idx = int(mut.strip()[1:-1])
                        base = mut[-1]
                        s = s[:idx - c.offset] + base + s[idx - c.offset +1:]
                    titles.append(';'.join(d.annotations['mutation']))
                else:
                    titles.append(cname)
                sequences.append(s)

                b = [str(x) for x in d.values]
                bonuses_1d.append(b)
                if ('clipsequence' in request.POST):
                    offset = seqpos_min
                    offset_seqpos.append([i - offset for i in c.seqpos])
                else:
                    offset = c.offset + 1
                    offset_seqpos.append([i - offset for i in c.seqpos])

                if is_2d:
                    if len(bonuses_2d) == 0:
                        bonuses_2d = zeros([len(seq), len(seq)])
                    for i, pos in enumerate(c.seqpos):
                        bonuses_2d[pos - offset, idx - offset] = d.values[i]
                        
                if is_modified:
                    modifiers.append(modifier)
                else:
                    modifiers.append(','.join(d.annotations['modifier']))

    return (messages, valerrors, bonuses_1d, bonuses_2d, titles, modifiers, offset_seqpos, temperature, sequences, refstruct)


def fill_predict_form(request, sequences, structures, temperature, refstruct, bonuses_1d, bonuses_2d, modifiers, titles, offset_seqpos):
    form_params = {}

    form_params['sequences'] = ''
    form_params['structures'] = ''
    form_params['refstruct'] = refstruct.dbn
    form_params['temperature'] = str(temperature)
    if 'nbootstraps' in request.POST:
        form_params['nbootstraps'] = request.POST['nbootstraps']
    else:
        form_params['nbootstraps'] = '100'

    for i, seq in enumerate(sequences):
        if i < len(sequences):
            form_params['sequences'] += '>%s\n%s\n' % (titles[i], seq.upper())
        if i < len(structures):
            form_params['structures'] += '>%s\n%s\n' % (titles[i], structures[i])

    form_params['bonuses_1d'] = ''
    form_params['slope_1d'] = request.POST['slope_1d']
    form_params['intercept_1d'] = request.POST['intercept_1d']
    form_params['slope_2d'] = request.POST['slope_2d']
    form_params['intercept_2d'] = request.POST['intercept_2d']

    for i, md in enumerate(bonuses_1d):
        if len(md) > 0:
            tmpmd = mapping.MappingData(data=md, seqpos=offset_seqpos[i])
        form_params['bonuses_1d'] += '#Sample %s \n %s\n' % (i+1, str(tmpmd) )

    form_params['bonuses_2d'] = '\n'.join([' '.join([str(item) for item in row]) for row in bonuses_2d])
    form_params['annotations'] = '\n'.join(modifiers)

    if 'DMS' in modifiers:
        form_params['modtype'] = 'DMS'
    elif 'SHAPE' in modifiers or '1M7' in modifiers or 'NMIA' in modifiers:
        form_params['modtype'] = 'SHAPE'
    elif 'CMCT' in modifiers:
        form_params['modtype'] = 'CMCT'

    form = PredictionForm(form_params)
    return form


def bootstrap_annotations(mol, data, nbootstraps, fold_opts, bonus2d):
    ba = mol.bootstrap(data, nbootstraps, fold_opts=fold_opts, replacement=True, bonus2d=bonus2d)
    for b in ba:
        if ba[b] == None:
            ba[b] = '0.0%'
        else:
            ba[b] = str(ba[b]) + '%'
    return ba


def predict_run_1D_NN(request, sequences, mapping_data, structures, other_options, messages):
    is_1D = (request.POST['predtype'] == '1D')
    is_apply_bonus = is_1D
    slope = float(request.POST['slope_1d'])
    intercept = float(request.POST['intercept_1d'])
    bonus_options = ' -sm %s -si %s ' % (slope, intercept)

    if is_1D:
        modtype = request.POST['modtype']
        parsed_data = []
        parsed_seqpos = []
        try:
            for line in request.POST['bonuses_1d'].split('\n'):
                if len(line.strip()) == 0:
                    continue
                if line[0] == '#':
                    if len(parsed_data) > 0:
                        mapping_data.append(mapping.MappingData(data=parsed_data, seqpos=parsed_seqpos))
                    parsed_data = []
                    parsed_seqpos = []
                else:
                    items = line.split()
                    if len(items) > 2:
                        raise ValueError('Invalid input')
                    parsed_seqpos.append(int(items[0]) - 1)
                    if 'raw_bonuses' in request.POST:
                        term = exp((float(items[-1]) - intercept)/slope) - 1
                        parsed_data.append(term)
                    else:
                        parsed_data.append(float(items[-1]))
            mapping_data.append(mapping.MappingData(data=parsed_data, seqpos=parsed_seqpos))
        except Exception:
            messages.append('ERROR: Invalid bonus input format. No BONUS applied.')
            is_apply_bonus = False

    numitems = min(len(mapping_data), len(sequences))
    if numitems != len(mapping_data) and is_apply_bonus:
        messages.append('WARNING: SEQUENCE (more) and BONUS number mismatch. Only SEQUENCE with available BONUS were used.')
        mapping_data = mapping_data[:numitems]
    if numitems != len(sequences) and is_apply_bonus:
        messages.append('WARNING: SEQUENCE and BONUS (more) number mismatch. Only BONUS with available SEQUENCE were used.')
        sequences = sequences[:numitems]

    base_annotations = []

    for i, s in enumerate(sequences):
        if is_apply_bonus:
            predstructs = secondary_structure.fold(s.sequence, modifier=modtype, mapping_data=mapping_data[i], fold_opts=bonus_options+other_options)
        else:
            predstructs = secondary_structure.fold(s.sequence)
        if predstructs:
            struct = predstructs[0]
        else:
            struct = secondary_structure.SecondaryStructure(dbn='.'*len(s))
        structures.append(struct)

        if ('nbootstraps' in request.POST) and is_apply_bonus:
            if not request.POST['nbootstraps']:
                nbootstraps = 100
                messages.append('WARNING: invalid BOOTSTRAP number. Used default 100 instead.')
            else:
                nbootstraps = int(request.POST['nbootstraps'])
            ba = bootstrap_annotations(s, mapping_data[i], nbootstraps, other_options, False)
            base_annotations.append(ba)

    return (base_annotations, structures, mapping_data, messages)


def predict_run_2D(request, sequences, titles, structures, other_options, messages):
    slope = float(request.POST['slope_2d'])
    intercept = float(request.POST['intercept_2d'])
    bonus_options = ' -xs %s -xo %s ' % (slope, intercept)

    seq = sequences[0]
    sequences = [seq]
    titles = [titles[0] + ':2D bonuses']
    if len(structures) > 0:
        structures = [structures[0]]

    data = zeros([len(seq), len(seq)])
    rows = request.POST['bonuses_2d'].split('\n')
    if len(rows) != len(seq):
        messages.append('ERROR: 2D BONUS and (first) SEQUENCE size mismatch. No BONUS applied.')
    else:
        for i, row in enumerate(rows):
            items = row.split()
            if len(items) != len(seq):
                messages.append('ERROR: 2D BONUS and (first) SEQUENCE size mismatch. No BONUS applied.')
                data = zeros([len(seq), len(seq)])
                break
            for j, item in enumerate(items):
                data[i,j] = float(item)

    if 'applyzscores' in request.POST:
        bins = [i for i in range(data.shape[0]) if len(data[i,:] != 0) > 0]
        data = quick_norm(data, bins=bins[10:-10])
        zdata = zscores_by_row(data, slope, intercept)
        means = array([data[i,data[i,:] != 0].mean() for i in range(data.shape[0])])
        zdata[means > 0.2, :] = 0
        zdata[zdata < 0] = 0
        zdata = -abs(zdata)
    else:
        zdata = data
    zdata = zdata.T

    base_annotations = []
    predstructs = secondary_structure.fold(seq.sequence, mapping_data=zdata, fold_opts=bonus_options+other_options, bonus2d=True)
    if predstructs:
        struct = predstructs[0]
    else:
        struct = secondary_structure.SecondaryStructure(dbn='.'*len(seq))
    if request.POST['nbootstraps']:
        ba = bootstrap_annotations(seq, zdata, int(request.POST['nbootstraps']), bonus_options+other_options, True)
        base_annotations.append(ba)
    structures.append(struct)

    return (sequences, structures, messages, base_annotations)


