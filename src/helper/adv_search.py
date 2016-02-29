from django.shortcuts import render_to_response #, redirect

from rdatkit.view import VARNA
from rdatkit.mapping import MappingData
from rdatkit.secondary_structure import SecondaryStructure
from rdatkit.datahandlers import RDATFile, RDATSection, ISATABFile

from src.models import *

import datetime
import re

import simplejson
from pylab import *
#from mlabwrap import mlab


def render_structure(request):
    sequence = request.POST['sequence']
    structure =  request.POST['structure']
    offset = int(request.POST['offset'])
    seqpos = [int(s) - offset - 1 for s in request.POST['seqpos'].split(',')]
    data = array([float(x) for x in request.POST['colormap'].split(',')])
    adjusted_data = [ data.mean() if x < 0.01 else x for x in data]
    md = MappingData(data=adjusted_data, seqpos=seqpos)
    v = VARNA([sequence], [SecondaryStructure(dbn=structure)], mapping_data=[md])
    v.codebase = get_codebase(request)
    v.bpStyle = 'simple'
    v.baseInner = '#FFFFFF'
    v.baseOutline = '#FFFFFF'
    v.offset = request.POST['offset']
    v.width = 400
    v.height = 400
    return render_to_response('render_structure.html', {'panel':v.render(), 'title':request.POST['title']})


def advanced_search(): 
    other_errors = []
    check_structure_balance = False
    valid = True
    if request.method == 'POST':
        try:
            form = AdvancedSearchForm(request.POST)
            constructs_byquery = {}
            rdat_paths = {}
            rdats = {}
            query_data = {}
            construct_secstructelemdicts = {}
            searchid = randint(1, 10000)
            if 'structure' in request.POST and 'sequence' in request.POST:
                if len(request.POST['structure']) != len(request.POST['sequence']) and len(request.POST['structure']) > 0 and len(request.POST['sequence']) > 0:
                    other_errors.append('Structure and sequence motifs searched must have equal length')
                    valid =  False
            try:
                numresults = int(request.POST['numresults'])
            except:
                valid =  False

            if valid:
                for field in ('structure', 'sequence'):
                    if field in request.POST and request.POST[field]:
                        if field == 'structure':
                            if ' ' in request.POST[field]:
                                check_structure_balance = True
                            query_field = request.POST[field]
                            for ec in '.(){}':
                                query_field = query_field.replace(ec,'\\'+ec).replace('\\\\'+ec,ec)
                            if check_structure_balance:
                                query_field = query_field.replace(' ', '.*')
                            constructs_byquery[field] = ConstructSection.objects.filter(structure__regex=query_field)
                        if field =='sequence':
                            query_field = ''.join([toIUPACregex(s.upper()) for s in request.POST[field]])
                            constructs_byquery[field] = ConstructSection.objects.filter(sequence__regex=query_field)
                        query_data[field] = query_field
                if 'secstructelems' in request.POST:
                    query_data['secstructelems'] = request.POST.getlist('secstructelems')
                    all_constructs = ConstructSection.objects.all()
                    constructs_byquery['secstructelems'] = []
                    cids = []
                    for construct in all_constructs:
                        if structure_is_valid(construct.structure):
                            sstruct = SecondaryStructure(dbn=construct.structure)
                            ssdict = sstruct.explode()
                            for elem in query_data['secstructelems']:
                                if elem in ssdict and ssdict[elem]:
                                    cids.append(construct.id)
                                    construct_secstructelemdicts[construct.id] = ssdict
                                    break
                            constructs_byquery['secstructelems'] = ConstructSection.objects.filter(id__in=cids)
                if len(query_data) == 0: # No search criteria was chosen, get all constructs
                    constructs_byquery['all'] = ConstructSection.objects.all()
                    query_data['all'] = True

                if 'background_processed' in request.POST:
                    bp_entry_ids = [d.section.rmdb_id for d in EntryAnnotation.objects.filter(name='processing', value='backgroundSubtraction')]
                for field in constructs_byquery:
                    entry_types = request.POST.getlist('entry_type')
                    modifiers = request.POST.getlist('modifiers')
                    constructs_byquery[field].exclude(entry__latest=False)
                    for t, name in ENTRY_TYPE_CHOICES:
                        if t not in entry_types:
                            constructs_byquery[field] = constructs_byquery[field].exclude(entry__type=t)
                    for t, name in MODIFIERS:
                        if t not in modifiers:
                            constructs_byquery[field] = constructs_byquery[field].exclude(entry__rmdb_id__contains='_%s_' % t)
                    if 'include_eterna' not in request.POST:
                        constructs_byquery[field] = constructs_byquery[field].exclude(entry__from_eterna=True)
                    if 'background_processed' in request.POST:
                        constructs_byquery[field] = constructs_byquery[field].filter(entry__rmdb_id__in=bp_entry_ids)

                constructs = constructs_byquery.values()[0]
                for k, v in constructs_byquery.iteritems():
                    constructs = [c for c in constructs if c in v]

                entries_visited = []
                unique_constructs = []
                for c in constructs:
                    if c.entry.rmdb_id not in entries_visited:
                        unique_constructs.append(c)
                        entries_visited.append(c.entry.rmdb_id)
                rdat, all_values, cell_labels, values_min, values_max, values_min_heatmap, values_max_heatmap, unpaired_bins, paired_bins, unpaired_bin_anchors, paired_bin_anchors, rmdb_ids, messages, numallresults, render = get_restricted_RDATFile_and_plot_data(unique_constructs, numresults, query_data, searchid, construct_secstructelemdicts, check_structure_balance)
                
                rdat_path = 'search/%s.rdat' % searchid
                rdat.save(MEDIA_ROOT + '/data/' + rdat_path, version=0.24)

                return render_to_response(PATH.HTML_PATH['adv_search_res'], \
                        {'rdat_path':rdat_path, 'all_values':simplejson.dumps(all_values), 'values_min':values_min, 'values_max':values_max, \
                        'values_min_heatmap':values_min_heatmap, 'values_max_heatmap':values_max_heatmap, \
                        'rmdb_ids':simplejson.dumps(rmdb_ids), 'messages':messages, \
                        'unpaired_bins':simplejson.dumps(unpaired_bins), 'paired_bins':simplejson.dumps(paired_bins), \
                        'unpaired_bin_anchors':simplejson.dumps(unpaired_bin_anchors), 'paired_bin_anchors':simplejson.dumps(paired_bin_anchors), \
                        'render':render, 'render_paired_histogram':len(paired_bins) > 0, 'render_unpaired_histogram':len(unpaired_bins) > 0,\
                        'form':form, 'numresults':numallresults, 'cell_labels':simplejson.dumps(cell_labels), 'all_results_rendered':numallresults <= numresults},\
                        context_instance=RequestContext(request) )

        except ValueError as e:
            return render_to_response(PATH.HTML_PATH['adv_search_res'], {'render':False}, context_instance=RequestContext(request))

    else:
        form = AdvancedSearchForm()
    return render_to_response(PATH.HTML_PATH['adv_search'], {'form':form, 'other_errors':other_errors}, context_instance=RequestContext(request))


def get_restricted_RDATFile_and_plot_data(constructs, numresults, qdata, searchid, ssdict, check_structure_balance):
    rdat = RDATFile()
    all_values = []
    rmdb_ids = []
    values_min = float('Inf')
    values_max = float('-Inf')
    values_min_heatmap = float('Inf')
    values_max_heatmap = float('-Inf')
    messages = []
    paired_bins = []
    unpaired_bins = []
    paired_bin_anchors = []
    unpaired_bin_anchors = []
    paired_merged_data = []
    unpaired_merged_data = []
    cell_labels = []

    for k, c in enumerate(constructs):
        entry = RMDBEntry.objects.get(constructsection=c)
        seqpos = [int(i) for i in c.seqpos.strip('[]').split(',')]
        offset = int(c.offset)
        rseqpos_byquery = {}
        searchable_fields = {}
        seqpos_offset = min(seqpos) - offset - 1
        searchable_fields['sequence'] = ''.join([s for i, s in enumerate(c.sequence) if i + offset + 1 in seqpos])
        searchable_fields['structure'] = ''.join([s for i, s in enumerate(c.structure) if i + offset + 1 in seqpos])
        if 'all' in qdata:
            rseqposes = [seqpos]
        else:
            for field in qdata:
                if field in ('sequence', 'structure'):
                    matches = [range(m.start() + seqpos_offset, m.end() + seqpos_offset) for m in re.finditer(qdata[field], searchable_fields[field].upper())]
                    if check_structure_balance and field == 'structure':
                        field_seqpos = []
                        for match in matches:
                            if check_balance(''.join([c.structure[i] for i in match])):
                                field_seqpos.append([i + offset + 1 for i in match])
                    else:
                        field_seqpos = [[i + offset + 1 for i in match] for match in matches]
                    if 'motif' in rseqpos_byquery:
                        rseqpos_byquery['motif'] = [match for match in rseqpos_byquery['motif'] if match in field_seqpos]
                    else:
                        rseqpos_byquery['motif'] = field_seqpos
                if field == 'secstructelems':
                    rseqpos_byquery[field] = []
                    for elem in qdata[field]:
                        for poslist in ssdict[c.id][elem]:
                            rseqpos_byquery[field].append([i + offset + 1 for i in poslist])
            
            rseqposes = rseqpos_byquery.values()[0]
            for k, v in rseqpos_byquery.items():
                tmp = []
                for poslist1 in v:
                    for poslist2 in rseqposes:
                        poslist = []
                        for i in poslist1:
                            if i in poslist2:
                                if len(poslist) > 0 and i-1 in poslist or i+1 in poslist:
                                    poslist.append(i)
                                else:
                                    if len(poslist) > 0:
                                        tmp.append(poslist)
                                    poslist = []
                        if len(poslist) > 0:
                            tmp.append(poslist)
                rseqposes += tmp

        for secnum, rseqpos in enumerate(rseqposes):
            if len(rseqpos) > 0:
                rseqpos.sort()
                section = RDATSection()
                section.name = '%s:%s:%s' % (entry.rmdb_id, rseqpos[0], rseqpos[-1])
                section.offset = c.offset
                section.sequence = c.sequence
                section.structure = c.structure 
                section.annotations = {}
                section.xsel = []
                section.data = []
                section.mutpos = []
                section.data_types = []
                section.seqpos = rseqpos
                rdat.traces[section.name] = []
                rdat.xsels[section.name] = []
                rdat.values[section.name] = []
                rdat.errors[section.name] = []

                append_to_rdat = False
                for idx, datasection in enumerate(DataSection.objects.filter(construct_section=c)):
                    dsection = RDATSection()
                    parsedvalues = datasection.values.split(',')
                    dsection.values = [float(parsedvalues[seqpos.index(i)]) for i in rseqpos if i in seqpos]
                    valarray = array([float(p) for p in parsedvalues])
                    normvalarray = valarray#(valarray - valarray.mean())/valarray.std()
                    if len(dsection.values) == 0:
                        # No data on the required rseqpos, continue with next data
                        continue
                    else:
                        # We found at least one data section that has the required data, append the construct section to our rdat file
                        append_to_rdat = True
                    if len(datasection.errors) > 0:
                        parsederrors = datasection.errors.split(',')
                        dsection.errors = [float(parsederrors[seqpos.index(i)]) for i in rseqpos if i in seqpos]
                    else:
                        dsection.errors = []
                    if len(datasection.xsel) > 0:
                        parsedxsels = datasection.xsel.split(',')
                        dsection.xsel = [float(parsedxsels[seqpos.index(i)]) for i in rseqpos if i in seqpos]
                    else:
                        dsection.xsel = []

                    all_values.append([section.name + ':' + str(idx + 1)] + [normvalarray[seqpos.index(i)] for i in rseqpos if i in seqpos])
                    cell_labels.append([c.sequence[i - offset - 1] + c.structure[i - offset - 1] for i in rseqpos if i in seqpos])
                    if len(c.structure.strip()) > -1:
                        paired_merged_data += [normvalarray[seqpos.index(i)] for i in rseqpos if c.structure[i - offset -1] in ('(', ')') and i in seqpos]
                        unpaired_merged_data += [normvalarray[seqpos.index(i)] for i in rseqpos if c.structure[i - offset -1] == '.' and i in seqpos]
                    #values_min = min(values_min, min(dsection.values))
                    #values_max = max(values_max, max(dsection.values))
                    if datasection.trace:
                        dsection.traces = [float(d) for d in datasection.trace.split(',')]
                    else:
                        dsection.traces = []
                    if datasection.reads:
                        dsection.reads = [float(d) for d in datasection.reads.split(',')]
                    else:
                        dsection.reads = []
                    if append_to_rdat:
                        section.data.append(dsection)
                        rdat.traces[section.name].append(dsection.traces)
                        rdat.reads[section.name].append(dsection.reads)
                        rdat.values[section.name].append(dsection.values)
                        rdat.xsels[section.name].append(dsection.xsel)
                        rdat.errors[section.name].append(dsection.errors)
                        dsection.annotations = dict([(a.name, a.value) for a in DataAnnotation.objects.filter(section=datasection)])
                        rdat.constructs[section.name] = section
                        rmdb_ids.append(entry.rmdb_id)

    numallresults = len(all_values)
    rdat.loaded = True
    rdat.comments = 'Query results for %s in the Stanford RMDB on %s. Search id %s' % (qdata, datetime.datetime.now(), searchid)
    if len(rmdb_ids) > numresults:
        messages.append('Your query exceeded %s results, showing just the first %s' % (numresults, numresults))
    for v in all_values[:numresults]:
        values_min_heatmap = min(values_min_heatmap, min(v[1:]))
        values_max_heatmap = max(values_max_heatmap, max(v[1:]))
    if len(all_values) > 0:
        maxlen = max((len(row) for row in all_values[:numresults]))
    else:
        maxlen = 0
    for i in range(len(all_values)):
        if len(all_values[i]) < maxlen:
            all_values[i] += [float('NaN')]*(maxlen - len(all_values[i]))
    if len(rmdb_ids) > 0:
        values_max = 2
        values_min = -1
        paired_merged_data = array(paired_merged_data)
        unpaired_merged_data = array(unpaired_merged_data)
        paired_indices = logical_and(paired_merged_data >= values_min, paired_merged_data <= values_max)
        unpaired_indices = logical_and(unpaired_merged_data >= values_min, unpaired_merged_data <= values_max)
        if len(unpaired_merged_data) > 0:
            unpaired_bins, unpaired_bin_anchors = (x.tolist() for x in hist(unpaired_merged_data[unpaired_indices], 100)[:2])
        if len(paired_merged_data) > 0:
            paired_bins, paired_bin_anchors = (x.tolist() for x in hist(paired_merged_data[paired_indices], 100)[:2])
        row_length = len(all_values[0])
        render = True
    else:
        render = False
        row_length = 0
    return rdat, [['Position'] + [str(i+1) for i in range(row_length-1)]] + all_values[:numresults], cell_labels[:numresults], values_min, values_max, values_min_heatmap, values_max_heatmap, unpaired_bins, paired_bins, unpaired_bin_anchors, paired_bin_anchors, rmdb_ids[:numresults], messages, numallresults, render


IUPAC_dict = {'M':'[ACM]', 'R':'[AGR]','W':'[ATUW]','S':'[CGS]','Y':'[CTUY]','K':'[GUTK]','V':'[ACGV]','H':'[ACTUH]','D':'[AGTUD]','B':'[CGTUB]','X':'[GATUCX]','N':'[GAUTCN]'}


def toIUPACregex(s):
    if s in IUPAC_dict:
        return IUPAC_dict[s]
    return s


def check_balance(structure):
    stack = []
    for s in structure:
        if s == '(':
            stack.append(s)
        if s == ')':
            if len(stack) == 0:
                return False
            stack.pop()
    return len(stack) == 0


def structure_is_valid(struct):
    if '(' not in struct:
        return False
    stack = []
    for s in struct:
        if s == '(':
            stack.append(s)
        if s == ')':
            stack.pop()
        if s not in ['.',')','(']:
            return False
    return len(stack) == 0
