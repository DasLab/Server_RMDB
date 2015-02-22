from django.shortcuts import render_to_response #, redirect

from rdatkit.view import VARNA
from rdatkit.mapping import MappingData
from rdatkit.secondary_structure import SecondaryStructure
from rdatkit.datahandlers import RDATFile, RDATSection, ISATABFile

from rmdb.repository.models import *

import datetime
import re

import simplejson
from pylab import *
#from mlabwrap import mlab


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


def get_area_peaks():
	pass


def get_codebase(request):
	if 'mac' in request.META['HTTP_USER_AGENT']:
		codebase = 'http://rmdb.stanford.edu/site_media/bin/mac'
	else:
		codebase = 'http://rmdb.stanford.edu/site_media/bin'
	return codebase


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


def get_plot_data(construct, entry_type, maxlen):

	precalc_structures = '['
	accepted_tags = ['modifier', 'chemical', 'mutation', 'structure', 'lig_pos', 'MAPseq', 'EteRNA']
	try:
		datas = construct.datas
		seqpos = [int(x) for x in construct.seqpos.strip('][').split(',')]
		offset = construct.offset
		sequence = construct.sequence

		x_labels = ['%s%s' % (sequence[x-1-offset], x) for x in seqpos]
		y_labels = []
		row_limits = []
		data_matrix = []
		data_max = 0.
		data_min = 0.
		data_mean = []
		data_sd = 0.

		for i, data in enumerate(datas):
			annotations = data.annotations
			if 'structure' in annotations:
				precalc_structures += '"%s",' % annotations['structure']
				del(annotations['structure'])
			else:
				precalc_structures += '"%s",' % data.structure
			if entry_type == 'MM':
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
					y_label_tmp = '%s' % ','.join(annotations.values())
			elif entry_type == "MA":
				y_label_tmp = 'lig_pos:%s' % annotations["lig_pos"]
			elif entry_type == "SS" and "EteRNA" in annotations:
				y_label_tmp = '%s' % annotations["MAPseq"]
			else:
				annotations_flatten = [y for x in annotations.values() for y in x]
				y_label_tmp = '%s' % (','.join(annotations_flatten))
			y_labels.append(y_label_tmp)
			
			peaks_row = [float(x) for x in data.values.split(',')]
			data_max = max(max(peaks_row), data_max)
			data_min = min(min(peaks_row), data_min)

			y_min = 0
			y_max = max(peaks_row) + 0.5
			x_min = min(seqpos)
			x_max = max(seqpos)
			row_limits.append({'y_min':y_min, 'y_max':y_max, 'x_min':x_min, 'x_max':x_max})

			if data.errors.strip():
				errors_row = [float(x) for x in data.errors.split(',')]
			else:
				errors_row = [0.]*len(seqpos)

			for j in range(len(peaks_row)):
				seq = sequence[j]
				if 'mutation' in annotations:
					mutpos = annotations['mutation']
					for mut in mutpos:
						if seq == mut[0] and int(mut[1:-1]) == (j + offset + 1):
							seq = mut[-1]

				data_matrix.append({'x':i, 'y':j, 'value':peaks_row[j], 'error':errors_row[j], 'seq':seq})
				data_mean.append(peaks_row[j])

		precalc_structures = precalc_structures.strip(',') + ']'
		data_mean = array(data_mean)
		data_sd = std(data_mean)
		data_mean = mean(data_mean)
		print y_labels

	except ConstructSection.DoesNotExist:
		return None
	return {'data':data_matrix, 'peak_max':data_max, 'peak_min':data_min, 'peak_mean':data_mean, 'peak_sd':data_sd, 'row_lim':row_limits, 'x_labels':x_labels, 'y_labels':y_labels, 'precalc_structures':precalc_structures}


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


def get_font_size( labels ):
	font_size = 'small'
	if len( labels ) > 40: font_size = 'x-small'
	if len( labels ) > 80: font_size = 'xx-small'
	return font_size


def get_labels( construct_section ):
	labels = []
	for d in construct_section.data:
		label = ''
		for value_set in d.annotations.values():
			label = label + ' ' + ' '.join( value_set )
		if len( label ) > 40: label = label[:40]
		labels.append( label )
	return labels


def apply_ylabels( construct_section ):
	labels  = get_labels( construct_section )
	font_size = get_font_size( labels )
	yticks(range(len(labels)), labels, fontsize=font_size )


def apply_xlabels( construct_section ):
	seq = ''
	for i in construct_section.seqpos:
		seq += construct_section.sequence[i - construct_section.offset - 1]
		labels = ['%s%s' % (s,construct_section.seqpos[i]) for i, s in enumerate(seq)]
	font_size = get_font_size( labels )
	xticks(range(len(labels)), labels, rotation=90,fontsize=font_size)


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


