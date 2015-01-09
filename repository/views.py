from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, redirect
from django import forms

from rdatkit.datahandlers import RDATFile, RDATSection, ISATABFile
from rdatkit.secondary_structure import SecondaryStructure
from rdatkit.view import VARNA
from rdatkit.mapping import MappingData

from models import *
from helpers import *
from helper_stats import *
from settings import *

import datetime
from email.mime.text import MIMEText
from itertools import chain
import os
import re
import smtplib
from sys import stderr
from Tkinter import TclError

import simplejson
from pylab import *
import matplotlib
matplotlib.use('Agg')
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


def check_rmdb_id(id):
	m  = re.compile('\w{5,7}_\w{3,3}_\d{4,4}')
	if m.match(id):
		return True
	return False


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


def get_codebase(request):
	if 'mac' in request.META['HTTP_USER_AGENT']:
		codebase = 'http://rmdb.stanford.edu/site_media/bin/mac'
	else:
		codebase = 'http://rmdb.stanford.edu/site_media/bin'
	return codebase


def send_mail_to_staff(subject, content):
	msg = MIMEText(content)
	msg['Subject']  = subject
	msg['To'] = 'dimenwarper@gmail.com'
	msg['From'] = 'stanfordrmdb@gmail.com'
	s = smtplib.SMTP('smtp.gmail.com:587')
	s.starttls()
	s.login('stanfordrmdb@gmail.com', 'daslab4ever')
	s.sendmail(msg['From'], msg['To'], msg.as_string())
	s.quit()


def get_area_peaks():
	pass


def get_spreadsheet(url):
	url = os.popen('curl '+url+' -L -I -s -o /dev/null -w %{url_effective}').read().strip().replace('%3D','=').replace('%26','&')
	idx=url.find('key=')
	if idx > 0:
		key = ''
		idx = idx + 4
		while url[idx] != '&' and idx < len(url):
			key += url[idx]
			idx += 1
		authkey = os.popen('curl https://www.google.com/accounts/ClientLogin \
							-d Email=stanfordrmdb@gmail.com -d Passwd=daslab4ever \
							-d accountType=HOSTED_OR_GOOGLE \
							-d source=Google-spreadsheet \
							-d service=wise | grep Auth | cut -d\= -f2').read().strip()
		os.popen('curl -L --silent --header "Authorization: GoogleLogin auth=%s"\
					"http://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%s&hl&exportFormat=xls" > /tmp/%s.xls' % (authkey, key, key))
		return '/tmp/%s.xls' % key
	else:
		return ''


def save_annotations(dictionary, section, cl):
	count = 0
	for d in dictionary:
		for value in dictionary[d]:
			a = cl()
			a.name = d.strip()
			if d.strip() == 'mutation' or d.strip() == 'sequence':
				count += 1
			a.value = str(value.decode('ascii', 'ignore'))
			a.section = section
			a.save()
	return count


def get_arrays(datas):
	values = []
	traces = []
	reads = []
	xsels = []
	errors = []
	for d in datas:
		values.append(d.values)
		traces.append(d.trace)
		reads.append(d.reads)
		xsels.append(d.xsel)
		errors.append(d.errors)
	return array(values), array(traces), array(reads), array(xsels), array(errors)


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


def index(request):
	news = NewsItem.objects.all().order_by('-date')[:10]
	(N_all, N_RNA, N_puzzle, N_eterna, N_constructs, N_datapoints) = get_rmdb_stats()

	return render_to_response('index.html', {'N_all':N_all, 'N_RNA':N_RNA, 'N_constructs':N_constructs, 'N_datapoints':N_datapoints, 'news':news}, context_instance=RequestContext(request))


def contact(request):
	return render_to_response('contact.html', {}, context_instance=RequestContext(request))


def tools(request):
	return render_to_response('tools.html', {}, context_instance=RequestContext(request))


def specs(request, section):
	if len(section) > 0:
		return  HttpResponseRedirect('/repository/specs#' + section)
	return render_to_response('specs.html', {}, context_instance=RequestContext(request))


def search(request):
	sstring = request.GET['searchtext'].strip()
	entriesbyname = RMDBEntry.objects.filter(constructsection__name__icontains=sstring)
	entriesbyid = RMDBEntry.objects.filter(rmdb_id__icontains=sstring)
	entriesbycomments = RMDBEntry.objects.filter(comments__icontains=sstring)
	entriesbydescription = RMDBEntry.objects.filter(description__icontains=sstring)
	entriesbydataannotation = RMDBEntry.objects.filter(constructsection__datasection__dataannotation__value__icontains=sstring)
	entriesbyannotation = RMDBEntry.objects.filter(entryannotation__value__icontains=sstring)
	combined_entries = list(chain(entriesbyname, entriesbyid, entriesbydescription, entriesbydataannotation, entriesbyannotation, entriesbycomments))
	entryids = []
	entries = []
	etypenames = dict(ENTRY_TYPE_CHOICES)
	for e in combined_entries:
		if e.rmdb_id not in entryids:
			e.constructs = ConstructSection.objects.filter(entry=e)
			e.short_description = e.comments
			e.typename = etypenames[e.type]
			entryids.append(e.rmdb_id)
			entries.append(e)
	return render_to_response('results.html', {'entries':entries, 'sstring':sstring}, context_instance=RequestContext(request))



def get_plot_data(construct_id, entry_type, maxlen):
	peaks = ''
	precalc_structures = '['
	accepted_tags = ['modifier', 'chemical', 'mutation', 'structure']
	try:
		construct = ConstructSection.objects.get(pk=construct_id)
		datas = DataSection.objects.filter(construct_section=construct).order_by('id')
		seqpos = construct.seqpos.strip('][').split(',')
		hist_data = []
		seqlabel = ['"%s%s"' % (s, construct.sequence[int(s)-1-construct.offset]) for s in seqpos]
		peaks = '[["Annotation", '+','.join(seqlabel) + '], '
		peak_max = 0.
		peak_min = 0.
		for i, data in enumerate(datas[:maxlen]):
			annotations = dict([(d.name, d.value) for d in DataAnnotation.objects.filter(section=data) if d.name in accepted_tags])
			if 'structure' in annotations:
				precalc_structures += '"%s",' % annotations['structure']
				del(annotations['structure'])
			else:
				precalc_structures += '"%s",' % data.structure
			values = '[' 
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
					values += '"%s",' % annotations[field]
				else:
					values += '"%s",' % ','.join(annotations.values())
			else:
				values += '"%s;%s",' % (i+1, ','.join(annotations.values()))
			values += ','.join(data.values.split(',')) + '], \n'
			parsed_peaks = [float(x) for x in data.values.split(',')]
			if max(parsed_peaks) > peak_max:
				peak_max = max(parsed_peaks)
			if min(parsed_peaks) > peak_min:
				peak_min = min(parsed_peaks)
			if entry_type == 'SS':
				hist_peaks = parsed_peaks
				ymin = 0
				ymax = max(hist_peaks) + 0.5
				hist_pos = [int(x) for x in seqpos]
				xmin = min(hist_pos)
				xmax = max(hist_pos)
				title = ','.join(annotations.values())
				hist_labels = [ x.replace('"', '') for x in seqlabel]
				if data.errors.strip():
					hist_errors = [float(x) for x in data.errors.split(',')]
				else:
					hist_errors = [0.]*len(seqpos)
				hist_dicts = []
				for i in range(len(hist_peaks)):
					hist_dicts.append({'position':hist_pos[i], 'value':hist_peaks[i], 'label':hist_labels[i], 'error':hist_errors[i]})
				hist_data.append((simplejson.dumps(hist_dicts), xmin, xmax, ymin, ymax, title))

			peaks += values
		peaks = peaks[:-2].strip(',') + ']'
		precalc_structures = precalc_structures.strip(',') + ']'
	except ConstructSection.DoesNotExist:
		None, None, None, None, None
	return peak_min, peak_max, peaks, hist_data, precalc_structures


def detail(request, rmdb_id):
	data_annotations_exist = False
	maxlen = 256
	maxlen_flag = False
	try:
		entry = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version')[0]
		comments = entry.comments.split('\n')
		entry.annotations = EntryAnnotation.objects.filter(section=entry)
		if entry.pdb_entries != None and len(entry.pdb_entries.strip()) > 0:
			entry.pdb_ids = [x.strip() for x in entry.pdb_entries.split(',')]
		else:
			entry.pdb_ids = []
			constructs = ConstructSection.objects.filter(entry=entry)
		for c in constructs:
			c.area_peaks_min, c.area_peaks_max, c.area_peaks, c.hist_data, c.precalc_structures  = get_plot_data(c.id, entry.type, maxlen)
			c.datas = DataSection.objects.filter(construct_section=c).order_by('id')
			#c.annotations = ConstructAnnotation.objects.filter(section=c)
			c.show_slideshow = entry.has_traces or entry.type in ['TT', 'SS']
			c.data_count = range(len(c.datas))
			if len(c.datas) > maxlen:
				c.datas = c.datas[:maxlen]
				maxlen_flag = True
			for d in c.datas:
				d.annotations = DataAnnotation.objects.filter(section=d).order_by('name')
				if d.annotations:
					data_annotations_exist = True
	except RMDBEntry.DoesNotExist:
		raise Http404
	
	return render_to_response('detail.html', {'codebase':get_codebase(request), 'entry':entry, 'constructs':constructs, 'publication':entry.publication, 'comments':comments, 'data_annotations_exist':data_annotations_exist, 'maxlen_flag':maxlen_flag}, context_instance=RequestContext(request))


def browse(request):
	(N_all, N_RNA, N_puzzle, N_eterna, N_constructs, N_datapoints) = get_rmdb_stats()

	constructs_general = get_rmdb_category('general')
	constructs_puzzle = get_rmdb_category('puzzle')
	constructs_eterna = get_rmdb_category('eterna')

	return render_to_response('browse.html', {'constructs_general':constructs_general, 'constructs_puzzle':constructs_puzzle, 'constructs_eterna':constructs_eterna, 'N_all':N_all, 'N_general':N_all-N_puzzle-N_eterna, 'N_puzzle':N_puzzle, 'N_eterna':N_eterna}, context_instance=RequestContext(request))


def validate(request):
	if request.method == 'POST':
		errors = []
		form = ValidateForm(request.POST, request.FILES)
		link = request.POST['link']
		if not link:
			uploadfile = request.FILES['file']
		if request.POST['type'] == 'rdat':
			rdatfile = RDATFile()
			if link:
				path = RDAT_FILE_DIR + link + '/' + link + '.rdat'
				if os.exists(path):
					rdatfile.load(open(path))
				else:
					errors = []
					errors.append('Your RMDB ID is invalid')
					form = ValidateForm()
					messages = []
					return render_to_response('validate.html', {'form':ValidateForm(), 'valerrors':errors,'messages':[]}, context_instance=RequestContext(request))
				rf = open('/tmp/%s'%uploadfile.name, 'w')
				rf.write(uploadfile.read())
				rf.close()
				rf = open('/tmp/%s'%uploadfile.name)
				rdatfile.load(rf)
			messages = rdatfile.validate()
		else:
			isatabfile = ISATABFile()
			if link:
				fname = get_spreadsheet(link)
				if fname:
					isatabfile.load(fname)
				else:
					errors = []
					errors.append('Your link to the ISATAB file is invalid')
					form = ValidateForm()
					messages = []
					return render_to_response('validate.html', {'form':ValidateForm(), 'valerrors':errors,'messages':[]}, context_instance=RequestContext(request))
			else:
				isf = open('/tmp/%s'%uploadfile.name, 'w')
				isf.write(uploadfile.read())
				isf.close()
				isatabfile.load('/tmp/%s'%uploadfile.name)
			messages = isatabfile.validate()
		if not messages:
			messages.append('LOOKS_GOOD! Your file has passed all tests.')
	else:
		messages = []
		errors = []
		form = ValidateForm()
	return render_to_response('validate.html', {'form':form, 'messages':messages}, context_instance=RequestContext(request))


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
			for k, v in rseqpos_byquery.iteritems():
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


def advanced_search(request):
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
					bp_entryids = [d.section.rmdb_id for d in EntryAnnotation.objects.filter(name='processing', value='backgroundSubtraction')]
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
						constructs_byquery[field] = constructs_byquery[field].filter(entry__rmdb_id__in=bp_entryids)

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
				rdat_path = '/search/%s.rdat' % searchid
				rdat.save(RDAT_FILE_DIR + rdat_path, version=0.24)
				return render_to_response('advanced_search_results.html', \
						{'rdat_path':rdat_path, 'all_values':simplejson.dumps(all_values), 'values_min':values_min, 'values_max':values_max, \
						'values_min_heatmap':values_min_heatmap, 'values_max_heatmap':values_max_heatmap, \
						'rmdb_ids':simplejson.dumps(rmdb_ids), 'messages':messages, \
						'unpaired_bins':simplejson.dumps(unpaired_bins), 'paired_bins':simplejson.dumps(paired_bins), \
						'unpaired_bin_anchors':simplejson.dumps(unpaired_bin_anchors), 'paired_bin_anchors':simplejson.dumps(paired_bin_anchors), \
						'render':render, 'render_paired_histogram':len(paired_bins) > 0, 'render_unpaired_histogram':len(unpaired_bins) > 0,\
						'form':form, 'numresults':numallresults, 'cell_labels':simplejson.dumps(cell_labels), 'all_results_rendered':numallresults <= numresults},\
						context_instance=RequestContext(request) )
		except ValueError as e:
			return render_to_response('advanced_search_results.html', {'render':False}, context_instance=RequestContext(request))

	else:
		form = AdvancedSearchForm()
	return render_to_response('advanced_search.html', {'form':form, 'other_errors':other_errors}, context_instance=RequestContext(request))


def encode_entry(entry):
	entry.annotations = EntryAnnotation.objects.filter(section=entry)
	entry.constructs = ConstructSection.objects.filter(entry=entry)
	for c in entry.constructs:
		c.datas = DataSection.objects.filter(construct_section=c)
		for d in c.datas:
			d.annotations = DataAnnotation.objects.filter(section=d)
	return RMDBJSONEncoder().default(entry)


def get_constructs_by_ids():
	constructs = [cdict.values()[0] for cdict in ConstructSection.objects.values('name').distinct()]
	return constructs


def api_fetch_entry(request, rmdb_id):
	try:
		entry = RMDBEntry.objects.get(rmdb_id=rmdb_id, latest=True)
	except RMDBEntry.DoesNotExist:
		return HttpResponse('null', mimetype='application/json')
	jsonstr = simplejson.dumps(encode_entry(entry))
	print jsonstr
	return HttpResponse(jsonstr, mimetype='application/json')


def api_all_entries(request):
	jsonres = '[' + ','.join([simplejson.dumps(encode_entry(entry)) for entry in RMDBEntry.objects.filter(latest=True)]) + ']'
	return HttpResponse(jsonres, mimetype='application/json')


def api_entries_by_organism(request, organism_id):
	jsonres = '[' + ','.join([simplejson.dumps(encode_entry(entry)) for entry in RMDBEntry.objects.filter(organism__taxonomy_id=organism_id, latest=True)]) + ']'
	return HttpResponse(jsonres, mimetype='application/json')


def api_entries_by_system(request, system_id):
	constructs = get_constructs_by_ids()
	try:
		id = int(system_id)
	except ValueError:
		return HttpResponse('[]')
	if id < 0 or id >= len(constructs):
		return HttpResponse('[]')
	jsonres = '[' + ','.join([simplejson.dumps(encode_entry(entry)) for entry in RMDBEntry.objects.filter(constructsection__name=constructs[id], latest=True)]) + ']'
	return HttpResponse(jsonres, mimetype='application/json')


def api_rmdb_ids_by_organism(request, organism_id):
	jsonres = '[' + ','.join([entry.rmdb_id for entry in RMDBEntry.objects.filter(organism__taxonomy_id=organism_id, latest=True)]) + ']'
	return HttpResponse(jsonres, mimetype='application/json')


def api_rmdb_ids_by_system(request, system_id):
	constructs = get_constructs_by_ids()
	try:
		id = int(system_id)
	except ValueError:
		return HttpResponse('[]')
	if id < 0 or id >= len(constructs):
		return HttpResponse('[]')
	jsonres = '[' + ','.join([entry.rmdb_id for entry in RMDBEntry.objects.filter(constructsection__name=constructs[id], latest=True)]) + ']'
	return HttpResponse(jsonres, mimetype='application/json')


def api_all_rmdb_ids(request):    
	jsonres = '[' + ','.join(['"' + entry.rmdb_id + '"' for entry in RMDBEntry.objects.filter(latest=True)]) + ']'
	return HttpResponse(jsonres, mimetype='application/json')


def api_all_organisms(request):
	jsonres = '[' + ','.join([simplejson.dumps(RMDBJSONEncoder().default(o)) for o in Organism.objects.all()]) + ']'
	return HttpResponse(jsonres, mimetype='application/json')


def api_all_systems(request):
	constructs = get_constructs_by_ids()
	jsonres = '[' + ','.join([simplejson.dumps({'id':i, 'name':n}) for i, n in enumerate(constructs)]) + ']'
	return HttpResponse(jsonres, mimetype='application/json')


@login_required
def upload(request):
	other_errors = []
	if request.method == 'POST':
		try:
			form = UploadForm(request.POST, request.FILES)
			if form.is_valid():
				proceed = True
				if not check_rmdb_id(form.cleaned_data['rmdb_id']):
					other_errors.append('Your RMDB ID is not valid')
					proceed = False
				else:
					isatabfile = ISATABFile()
					rdatfile = RDATFile()
					rdatfile.loaded = False
					isatabfile.loaded = False
					uploadfile = request.FILES['file']
					rf = open('/tmp/%s'%uploadfile.name, 'w')
					rf.write(uploadfile.read())
					rf.close()
					rf = open('/tmp/%s'%uploadfile.name)
					if form.cleaned_data['filetype'] == 'isatab':
						isatabfile = ISATABFile()
						try:
							isatabfile.load(rf.name)
							isatabfile.loaded = True
							rdatfile = isatabfile.toRDAT()
						except Exception:
							other_errors.append('Your ISATAB file does not seem to be valid; please check and resubmit')
							proceed = False
					else:
						try:
							rdatfile.load(rf)
							rdatfile.loaded = True
							isatabfile = rdatfile.toISATAB()
						except None:
							print e
							other_errors.append('Your RDAT file does not seem to be valid; please check and resubmit')
							proceed = False

				if proceed:
					publication = Publication()
					publication.title = form.cleaned_data['publication']
					publication.authors = form.cleaned_data['authors']
					publication.pubmed_id = form.cleaned_data['pubmed_id']
					publication.save()
					datacount = 0
					constructcount = 0
					entries = RMDBEntry.objects.filter(rmdb_id=form.cleaned_data['rmdb_id'].upper()).order_by('-version')
					if len(entries) > 0:
						prev_entry = entries[0]
						current_version = prev_entry.version
						owner = prev_entry.owner
					else:
						current_version = 0
						owner = None
					if current_version > 0 and False: #owner != request.user:
						other_errors.append('RMDB entry %s exists and you cannot update it since you are not the owner' % request.POST['rmdb_id'])
						return render_to_response('upload.html', {'form':form, 'other_errors':other_errors}, context_instance=RequestContext(request))
					entry = RMDBEntry()
					entry.comments = rdatfile.comments
					entry.publication = publication
					entry.authors = form.cleaned_data['authors']
					entry.description = form.cleaned_data['description']
					entry.type = form.cleaned_data['type']
					entry.rmdb_id = form.cleaned_data['rmdb_id'].upper()
					entry.datacount = 0
					entry.constructcount = 0
					if request.user.is_staff:
						entry.revision_status = 'PUB'
					else:
						entry.revision_status = 'REV'
					entry.owner = request.user
					entry.version = current_version + 1
					if current_version == 0:
						entry.latest = True 
					entry.save()
					if not os.path.exists('%s%s' % (RDAT_FILE_DIR, entry.rmdb_id)):
						os.mkdir('%s%s' % (RDAT_FILE_DIR, entry.rmdb_id))
					if not os.path.exists('%s%s' % (ISATAB_FILE_DIR, entry.rmdb_id)):
						os.mkdir('%s%s' % (ISATAB_FILE_DIR, entry.rmdb_id))
					rdatname = '%s%s/%s_%s.rdat' % (RDAT_FILE_DIR, entry.rmdb_id, entry.rmdb_id, entry.version)
					os.popen('mv /tmp/%s %s' % (uploadfile.name, rdatname))
					os.popen('cp %s %s%s/%s.rdat' % (rdatname, RDAT_FILE_DIR, entry.rmdb_id, entry.rmdb_id))
					os.popen('cp %s %s%s/%s_synced.rdat' % (rdatname, RDAT_FILE_DIR, entry.rmdb_id, entry.rmdb_id))
					# Breaks Excel compatibility if data/columns are > 256
					if len(rdatfile.values.values()[0]) < 256:
						isatabfile.save('%s%s/%s_%s.xls' % (ISATAB_FILE_DIR, entry.rmdb_id, entry.rmdb_id, entry.version))
					save_annotations(rdatfile.annotations, entry, EntryAnnotation)
					for k in rdatfile.constructs:
						constructcount += 1
						c = rdatfile.constructs[k]
						construct = ConstructSection()
						construct.entry = entry
						construct.name = c.name
						construct.sequence = c.sequence
						construct.offset = c.offset
						construct.structure = c.structure
						construct.seqpos = ','.join([str(x) for x in c.seqpos])
						construct.xsel = ','.join([str(x) for x in c.xsel])
						construct.save()
						#save_annotations(c.annotations, construct, ConstructAnnotation)
						for d in c.data:
							data = DataSection()
							data.xsel = ','.join([str(x) for x in d.xsel])
							data.values = ','.join([str(x) for x in d.values])
							data.errors = ','.join([str(x) for x in d.errors])
							datacount += len(d.values)
							data.trace = ','.join([str(x) for x in d.trace])
							data.reads = ','.join([str(x) for x in d.reads])
							entry.has_trace = False
							data.seqpos = ','.join([str(x) for x in d.seqpos])
							data.construct_section = construct
							data.save()
							constructcount += save_annotations(d.annotations, data, DataAnnotation)
						entry.datacount = datacount
						entry.constructcount = constructcount
						try:
							entry.has_traces = generate_images(construct, c, entry.type, engine='matplotlib')
						except TclError:
							other_errors.append('Problem generating the images. This is a server-side problem, please try again.')
							proceed = False
						entry.save()
						generate_varna_thumbnails(entry)
						#precalculate_structures(entry)

					send_mail_to_staff('New RMDB entry submitted!', 'Entry %s has just been submitted for review by user %s. \
						please go to the admin page of this entry (http://rmdb.stanford.edu/admin/repository/rmdbentry/%s) and check its associated files in RDAT \
						(http://rmdb.stanford.edu/site_media/rdat_files/%s/%s_synced.rdat) and Isa-TAB (http://rmdb.stanford.edu/site_media/isatab_files/%s/%s_%s.xls) formats. \n\n -The RMDB Team' % \
						(entry.rmdb_id, request.user.username, entry.id, entry.rmdb_id, entry.rmdb_id, entry.rmdb_id, entry.rmdb_id, entry.version))
					return HttpResponseRedirect('/repository/detail/%s'%entry.rmdb_id)

		except IndexError:
			other_errors.append('Your file does not seem to be valid; please check and resubmit')
			print e
	else:
		form = UploadForm()
	return render_to_response('upload.html', {'form':form, 'other_errors':other_errors}, context_instance=RequestContext(request))


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


# def generate_images(construct_model, construct_section, entry_type, engine='matplotlib'):
# 	dir = CONSTRUCT_IMG_DIR+'%s/'%construct_model.id
# 	if not os.path.exists(dir):
# 		os.mkdir(dir)
# 	values_array, trace_array, xsel_array, errors_array = get_arrays(construct_section.data)
# 	values_dims = shape(values_array)
# 	trace_dims = shape(trace_array)
# 	values_mean = values_array.mean(axis=0)
# 	values_std = values_array.std(axis=0)
# 	if engine == 'matplotlib':
# 		if size(trace_array) > 0:
# 			figure(2)
# 			aspect_ratio = "auto"
# 			if (entry_type == 'MM'):  aspect_ratio = shape( trace_array )[1] / float( shape( trace_array)[0]  )
# 			imshow(trace_array, cmap=get_cmap('Greys'), vmin=0, vmax=trace_array.mean(), aspect=aspect_ratio, interpolation='nearest')
# 			#apply_xlabels( construct_section )
# 			xticks( [],[] )
# 			apply_ylabels( construct_section )
# 			savefig(dir+'/trace.png')
# 			has_traces = True
# 		else:
# 			has_traces = False

# 		figure(2)
# 		clf()

# 		aspect_ratio = "auto"
# 		if (entry_type == 'MM'):  aspect_ratio = "equal" #aspect_ratio = shape(values_array)[0]/ float( shape( values_array )[1] )

# 		#imshow(values_array, cmap=get_cmap('Greys'), vmin=0, vmax=values_array.mean(), aspect=aspect_ratio, interpolation='nearest')
# 		imshow(values_array, cmap=get_cmap('Greys'), vmin=0, vmax=values_array.max(), aspect=aspect_ratio, interpolation='nearest')

# 		apply_xlabels( construct_section )
# 		apply_ylabels( construct_section )
# 		ylim( [-0.5, shape( values_array )[0]-0.5  ] )
# 		savefig(dir+'/values.png')

# 		figure(1)
# 		clf()
# 		#matshow(corrcoef(values_array.T)**10)
# 		#savefig(dir+'/corrcoef.png')
# 		if entry_type == 'SS':
# 			for j in range(values_dims[0]):
# 				figure(1)
# 				clf()
# 				yerr=errors_array[j,:]
# 				if len( yerr ) == 0:
# 				yerr = values_array[j,:]*0.01 #placeholder
# 				yval = values_array[j,:]
# 				for m in range( len( yval) ):
# 				if yval[m] < 0.0: yval[m] = 0.0
# 				bar(range(values_dims[1]), yval, yerr)
# 				bartitle = ''
# 				for vals in  construct_section.data[j].annotations.values(): bartitle += ' '.join( vals )
# 				suptitle( bartitle )
# 				apply_xlabels( construct_section )
# 				xlim( [0, shape( values_array )[1] ] )
# 				savefig(dir+'/barplot%s.png'%j)


# 	elif engine == 'matlab':
# 		h = mlab.figure(1)
# 		mlab.clf()
# 		mlab.colormap( 1 - mlab.gray(100));
# 		mlab.image( 100 * trace_array/trace_array.mean().mean()  )
# 		mlab.saveas(h, dir+'/trace.png')
# 		h = mlab.figure(2)
# 		mlab.clf()
# 		mlab.colormap( 1 - mlab.gray(100));
# 		mlab.image( 100 * values_array/values_array.mean().mean()  )
# 		mlab.saveas(h, dir+'/values.png')
# 		figure(3)
# 		clf()
# 		hist(values_array.reshape(size(values_array)), 50)
# 		savefig(dir+'/values_hist.png')
# 		figure(3)
# 		clf()
# 		hist(trace_array.reshape(size(trace_array)), 50)
# 		savefig(dir+'/trace_hist.png')
# 		figure(1)
# 		clf()
# 		matshow(corrcoef(values_array.T)**10)
# 		savefig(dir+'/corrcoef.png')
# 		figure(1)
# 		clf()
# 		bar(range(values_dims[1]), values_mean, yerr=values_std)
# 		seq = ''
# 		for i in construct_section.seqpos:
# 		seq += construct_section.sequence[i - construct_section.offset]
# 		labels = ['%s%s' % (s,construct_section.seqpos[i]) for i, s in enumerate(seq)]
# 		xticks(range(len(labels)), labels, rotation=90)
# 		savefig(dir+'/barplot.png')
# 	else:
# 		raise Exception('Uknown plotting engine '+engine)
# 	return has_traces


def user_login(request):
	if 'next' in request.GET:
		next = request.GET['next']
	else:
		next = '/repository/'
	if request.method == 'POST':
		form = LoginForm(request.POST)
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(next)
			else:
				return render_to_response('login.html', {'form':form, 'error_msg':'This account has been disabled', 'next':next}, context_instance=RequestContext(request))
		else:
			return render_to_response('login.html', {'form':form, 'error_msg':'Username and/or password incorrect', 'next':next}, context_instance=RequestContext(request))
	else:
		form = LoginForm()
		return render_to_response('login.html', {'form':form, 'error_msg':'', 'next':next}, context_instance=RequestContext(request))


def register(request):
	other_errors = []
	if request.method == 'POST':
		validated = True
		form = RegistrationForm(request.POST)
		if form.is_valid():
			if form.cleaned_data['password'] == form.cleaned_data['repeatpassword']:
				user =  User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
				rmdbuser = RMDBUser()
				user.first_name = form.cleaned_data['firstname']
				user.last_name = form.cleaned_data['lastname']
				user.set_password(form.cleaned_data['password'])
				user.is_active = True
				user.save()
				rmdbuser.user = user
				rmdbuser.institution = form.cleaned_data['institution']
				rmdbuser.department = form.cleaned_data['department']
				rmdbuser.save()
				authuser = authenticate(username=user.username, password=form.cleaned_data['password'])
				login(request, authuser)
				return HttpResponseRedirect('/repository/')
			else:
				other_errors.append('Password fields do not match')
	else:
		form = RegistrationForm()
	return render_to_response('registration.html', {'form':form, 'other_errors':other_errors})


def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/repository/')

