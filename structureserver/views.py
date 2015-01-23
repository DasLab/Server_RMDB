from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django import forms

from rdatkit.datahandlers import RDATFile, ISATABFile
from rdatkit import rna, secondary_structure, mapping, view

from rmdb.repository.models import RMDBEntry
from rmdb.repository.settings import *
from settings import *
from models import *

from filtertools import *
from numpy import *
from scipy.stats import stats
import simplejson

import os
import tempfile


def bpdict_to_str(d):
	res = ''
	for bp in d:
		res += '%s,%s,%s;' % (bp[0], bp[1], d[bp])
	return res.strip(';')


def str_to_bpdict(s):
	res = {}
	for e in s.split(';'):
		fields = e.split(',')
		res[(fields[0], fields[1])] = fields[2]
	return res


def normalize(bonuses):
	l = len(bonuses)
	wtdata = array(bonuses)
	if wtdata.min() < 0:
		wtdata -= wtdata.min()
	interquart = stats.scoreatpercentile(wtdata, 75) - stats.scoreatpercentile(wtdata, 25)
	for i in range(l):
		if wtdata[i] > interquart*1.5:
			wtdata[i] = 999
	tenperc = stats.scoreatpercentile(wtdata, 90)
	maxcount = 0
	maxav = 0.
	for i in range(l):
		if wtdata[i] >= tenperc:
			maxav += wtdata[i]
			maxcount += 1
	maxav /= maxcount
	wtdata = wtdata/maxav
	return wtdata


def bootstrap_annotations(mol, data, nbootstraps, fold_opts, bonus2d):
	ba = mol.bootstrap(data, nbootstraps, fold_opts=fold_opts, replacement=True, bonus2d=bonus2d)
	for b in ba:
		if ba[b] == None:
			ba[b] = '0.0%'
		else:
			ba[b] = str(ba[b]) + '%'
	return ba


def index(request):
	if request.method == 'POST':
		try:
			imgname = ''
			sequences = []
			titles = []
			structures =[]
			modifiers = []
			mapping_data = []
			base_annotations = []
			messages = []
			valerrors = []
			if ('rmdbid' in request.POST and request.POST['rmdbid']) or 'rdatfile' in request.FILES:
				temperature = 37
				offset_seqpos = []
				rdatfile = RDATFile()
				if 'rdatfile' in request.FILES:
					uploadfile = request.FILES['rdatfile']
					rf = open('/tmp/%s'%uploadfile.name, 'w')
					rf.write(uploadfile.read())
					rf.close()
					rf = open('/tmp/%s'%uploadfile.name)
				else:
					rmdbid = request.POST['rmdbid'].strip()
					version = RMDBEntry.get_current_version(rmdbid)
					rf = open(RDAT_FILE_DIR + '/%s/%s_%s.rdat' % (rmdbid, rmdbid, version))
				rdatfile.load(rf)
				modifieddata = 'modifier' in rdatfile.annotations
				if modifieddata:
					modifier = ','.join(rdatfile.annotations['modifier'])
				refstruct = secondary_structure.SecondaryStructure()
				for cname in rdatfile.constructs:
					if len(sequences):
						messages.append('Warning: Received an RDAT file plus input sequences. \
						Ignoring input sequences, and showing only RDAT file content.')
						sequences = []
						titles = []
					if len(structures):
						messages.append('Warning: Received an RDAT file plus input structures. \
						Ignoring input structures, and showing only RDAT file content.')
						structures = []
					c = rdatfile.constructs[cname]
					if 'temperature' in c.annotations:
						temperature = c.annotations['temperature']
					seq = ''
					idxs = []
					bonuses_1d = []
					if len(c.sequence) >= max(c.seqpos) - c.offset-1:
						clippedseq = ''.join([c.sequence[i - c.offset-1] for i in sorted(c.seqpos)])
					else: 
						valerrors.append('Warning: Construct %s in RDAT file has a sequence that is missing nucleotides defined in SEQPOS, ignoring SEQPOS' % c.name)
						c.seqpos = [i+1 for i in range(len(c.sequence))]
						clippedseq = c.sequence
					if len(c.structure) >= max(c.seqpos) - c.offset-1:
						clippedstruct = ''.join([c.structure[i - c.offset-1] for i in sorted(c.seqpos)])
					else:
						valerrors.append('Warning: Construct %s in RDAT file has no expected secondary structure or has a structure that does not match SEQPOS, filling out a trivial structure instead' % c.name)
						clippedstruct = '.'*(max(c.seqpos) - c.offset-1)
						c.structure = clippedstruct
					seqposmin = min(c.seqpos)
					bonuses_2d = []
					if 'clipsequence' in request.POST:
						seq = clippedseq
						struct = clippedstruct
					else:
						seq = c.sequence
						struct = c.structure
					if len(refstruct) == 0:
						refstruct = secondary_structure.SecondaryStructure(dbn=struct)
					for d in c.data:
						if modifieddata or 'modifier' in d.annotations:
							s = seq
							add_to_2d_bonuses = False
							if 'mutation' in d.annotations:
								for mut in d.annotations['mutation']:
									if 'WT' == mut.strip():
										break
									add_to_2d_bonuses = True
									idx = int(mut.strip()[1:-1])
									base = mut[-1]
									s = s[:idx - c.offset] + base + s[idx - c.offset +1:]
								titles.append(';'.join(d.annotations['mutation']))
							else:
								titles.append(cname)
							sequences.append(s)
							b = [str(x) for x in d.values]
							bonuses_1d.append(b)
							if 'clipsequence' in request.POST:
								offset = seqposmin
								offset_seqpos.append([i - offset for i in c.seqpos])
							else:
								offset = c.offset + 1
								offset_seqpos.append([i - offset for i in c.seqpos])
							if add_to_2d_bonuses:
								if len(bonuses_2d) == 0:
									bonuses_2d = zeros([len(seq), len(seq)])
								for i, pos in enumerate(c.seqpos):
									bonuses_2d[pos - offset, idx - offset] = d.values[i]
							if modifieddata:
								modifiers.append(modifier)
							else:
								modifiers.append(','.join(d.annotations['modifier']))
				form_params = {}
				form_params['sequences'] = ''
				form_params['structures'] = ''
				form_params['refstruct'] = refstruct.dbn
				for i, seq in enumerate(sequences):
					if i < len(sequences):
						form_params['sequences'] += '>%s\n%s\n' % (titles[i], seq.upper())
					if i < len(structures):
						form_params['structures'] += '>%s\n%s\n' % (titles[i], structures[i])
				form_params['slope_1d'] = request.POST['slope_1d']
				form_params['intercept_1d'] = request.POST['intercept_1d']
				form_params['slope_2d'] = request.POST['slope_2d']
				form_params['intercept_2d'] = request.POST['intercept_2d']
				form_params['temperature'] = request.POST['temperature']
				form_params['bonuses_1d'] = ''
				form_params['temperature'] = str(temperature)
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
				return render_to_response('html/predict.html', {'form':form, 'rdatloaded':True, 'valerrors':valerrors})

	#======  End RDAT file and RMDB entry parsing ======

			otheroptions = ' -t %s ' % (float(request.POST['temperature']) + 273.15)
			refstruct = secondary_structure.SecondaryStructure(dbn=request.POST['refstruct'])
			modifiers = request.POST['annotations'].split('\n')
			lines = request.POST['sequences'].split('\n')
			print 'PREDTYPE '
			print request.POST['predtype']
			for l in lines:
				if l:
					if l[0] == '>':
						titles.append(l.replace('>',''))
					else:
						if l.strip():
							sequences.append(rna.RNA(l.strip())) 
			if 'structures' in request.POST:
				lines = request.POST['structures'].split('\n')
				for l in lines:
					if l.strip():
						structures.append(l)
			if not sequences:
				messages.append('No sequences found: This is either because you did not input any sequences or your RDAT file contains no chemically modified lanes')
				return render_to_response('html/predict_result.html', {'panels':[], 'messages':messages,'bppmimg':'', 'ncols':0, 'nrows':0}, context_instance=RequestContext(request))

			if request.POST['predtype'] == '1D':
				apply_bonuses = True
				slope = float(request.POST['slope_1d'])
				intercept = float(request.POST['intercept_1d'])
				modtype = request.POST['modtype']
				bonusoptions = ' -sm %s -si %s ' % (slope, intercept)
				drawbppm = True
				lenseqs = len(sequences[0])
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
								print term
								parsed_data.append(exp((float(items[-1]) - intercept)/slope) - 1)
							else:
								parsed_data.append(float(items[-1]))
					mapping_data.append(mapping.MappingData(data=parsed_data, seqpos=parsed_seqpos))
				except Exception:
					messages.append('Bonus input is in invalid format (please use RNAstructure format for bonuses). Bonuses have not been applied to prediction!')
					apply_bonuses = False
				for s in sequences:
					if len(s) != lenseqs:
						drawbppm = False
				if drawbppm:
					finalbppm = zeros([lenseqs, lenseqs])
				numitems = min(len(mapping_data), len(sequences))
				if numitems != len(mapping_data) and apply_bonuses:
					messages.append('Missing mapping data for one or more sequences. Currently showing sequences with data available')
					mapping_data = mapping_data[:numitems]
				if numitems != len(sequences) and apply_bonuses:
					messages.append('More mapping data entries than sequences found. Applied only relevant mapping data entries')
					sequences = sequences[:numitems]
				for i, s in enumerate(sequences):
					if apply_bonuses:
						predstructs = secondary_structure.fold(s.sequence, modifier=modtype, mapping_data=mapping_data[i], fold_opts=otheroptions)
					else:
						predstructs = secondary_structure.fold(s.sequence)
					if predstructs:
						struct = predstructs[0]
					else:
						struct = secondary_structure.SecondaryStructure(dbn='.'*len(s))
					structures.append(struct)
					if request.POST['nbootstraps_1d'] and apply_bonuses:
						ba = bootstrap_annotations(s, mapping_data[i], int(request.POST['nbootstraps_1d']), otheroptions)
						base_annotations.append(ba)
				"""
				os.popen(PARTCMD + ' ' + seqfile.name + ' blah.pfs -sh ' + shpfile.name + bonusoptions)
				shpfile.close()
				if drawbppm:
				bppm  = loadtxt(open('bpp.txt'))
				finalbppm = bppm + finalbppm
				structures.append(struct)
				imgname = ''
				drawbppm = False
				if drawbppm:
				figure(1)
				clf()
				matshow(finalbppm)
				imgname = tmpdir.replace('/','') +'.png'
				savefig('/home/daslab/rdat/rmdb/design/tmp/' + imgname)
				"""

			if request.POST['predtype'] == '2D':
				slope = float(request.POST['slope_2d'])
				intercept = float(request.POST['intercept_2d'])
				#bonusoptions = ' -xs %s -xo %s ' % (slope, intercept)
				bonusoptions = ''
				seq = sequences[0]
				data = zeros([len(seq), len(seq)])
				rows = request.POST['bonuses_2d'].split('\n')
				mapping_data = []
				titles = [titles[0] + ':2D bonuses']
				sequences = [seq]
				modifiers = ['']
				if len(structures) > 0:
					structures = [structures[0]]
#TODO This validation should be done client side
				if len(rows) != len(seq):
					messages.append('Size of 2D bonuses does not match with size of first sequence, bonuses have not been applied to prediction!')
				else:
					for i, row in enumerate(rows):
						items = row.split()
						if len(items) != len(seq):
							messages.append('Size of 2D bonuses does not match with size of first sequence, bonuses have not been applied to prediction!')
							data = zeros([len(seq), len(seq)])
							break
						for j, item in enumerate(items):
							data[i,j] = float(item)
				tmpdir = tempfile.mkdtemp(prefix=TMPDIR)
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
				mapping_data = []
				predstructs = secondary_structure.fold(seq.sequence, mapping_data=zdata.T, fold_opts=bonusoptions+otheroptions, bonus2d=True)
				if predstructs:
					struct = predstructs[0]
				else:
					struct = secondary_structure.SecondaryStructure(dbn='.'*len(seq))
				if request.POST['nbootstraps_2d']:
					base_annotations.append(bootstrap_annotations(seq, zdata, int(request.POST['nbootstraps_2d']), bonusoptions+otheroptions, True))
				structures.append(struct)
				imgname = ''
				"""
				bppm  = loadtxt(open('bpp.txt'))
				figure(1)
				clf()
				matshow(bppm)
				imgname = tmpdir.replace('/','') +'.png'
				savefig('/home/daslab/rdat/rmdb/design/tmp/' + imgname)
				"""

			if request.POST['predtype'] == 'NN':
				if len(sequences) > 1:
					messages.append('Warning: More than one sequence defined without bonuses, just taking the first one')
				seq = sequences[0]
				sequences = [seq]
				modifiers = [modifiers[0]]
				mapping_data = [] 
				titles = [titles[0]]
				if len(structures) > 0:
					structures = [structures[0]]
				predstructs = secondary_structure.fold(seq.sequence)
				if predstructs:
					struct = predstructs[0]
				else:
					struct = secondary_structure.SecondaryStructure(dbn='.'*len(seq))
				structures.append(struct)
				imgname = ''
				"""
				bppm  = loadtxt(open('bpp.txt'))
				figure(1)
				clf()
				matshow(bppm)
				imgname = tmpdir.replace('/','') +'.png'
				print sequences
				savefig('/home/daslab/rdat/rmdb/design/tmp/' + imgname)
				"""
			panels, ncols, nrows = render_to_varna([s.sequence for s in sequences], structures, modifiers, titles, mapping_data, base_annotations, refstruct)
			visform_params = {}
			visform_params['sequences'] = '\n'.join([s.sequence for s in sequences])
			visform_params['structures'] = '\n'.join([s.dbn for s in structures])
			if 'raw_bonuses' in request.POST:
				print [str(slope*log(1 + d) + intercept) for d in mapping_data[0].data()]
				visform_params['md_datas'] = '\n'.join([','.join([str(slope*log(1 + d) + intercept) for d in m.data()]) for m in mapping_data])
			else:
				visform_params['md_datas'] = '\n'.join([','.join([str(d) for d in m.data()]) for m in mapping_data])
			visform_params['md_seqposes'] = '\n'.join([','.join([str(pos) for pos in m.seqpos]) for m in mapping_data])
			visform_params['modifiers'] = modifiers
			visform_params['base_annotations'] = '\n'.join([bpdict_to_str(ann) for ann in base_annotations])
			visform_params['refstruct'] = refstruct.dbn
			visform = VisualizerForm(visform_params)
			return render_to_response('html/predict_result.html', {'panels':panels, 'messages':messages,'ncols':ncols, 'nrows':nrows, 'form':visform}, context_instance=RequestContext(request))
		except IndexError:
			print e
			return render_to_response('html/predict.html', {'form':PredictionForm(), 'rdatloaded':False, 'other_errors':['Invalid input. Please check your inputs and try again.']})

	else:
		form = PredictionForm()
		return render_to_response('html/predict.html', {'form':form, 'rdatloaded':False, 'other_errors':[]}, context_instance=RequestContext(request))


def render_to_varna(sequences, structures, modifiers, titles, mapping_data, base_annotations, refstruct):
	panels = []
	ncols = min(4, len(sequences))
	nrows = 4
	if ncols < 4:
		nrows = 1
	nelems = nrows * ncols
	for i in range(len(sequences)):
		v = view.VARNA(sequences[i:i+nelems], structures[i:i+nelems], mapping_data=mapping_data[i:i+nelems])
		v.title = titles[i:i+nelems]
		v.colorMapCaption = modifiers[i:i+nelems]
		v.codebase = 'http://rmdb.stanford.edu/site_media/bin'
		v.bpStyle = 'simple'
		v.baseInner = '#FFFFFF'
		v.baseOutline = '#FFFFFF'
		v.width = 400
		v.height = 600
		panels.append(v.render(base_annotations=base_annotations[i:i+nelems], annotation_by_helix=True, annotation_def_val='0.0%', helix_function=(lambda x, y: str(max(float(str(x).strip('%')), float(str(y).strip('%')))) + '%'), reference_structure=refstruct))
	return panels, ncols, nrows


def viewstructures(request):
	if request.method == 'POST':
		sequences = request.POST['sequences'].split('\n')
		titles  = request.POST['titles'].split('\n')
		dbns = request.POST['structures'].split('\n')
		md_seqposes = request.POST['md_seqposes'].split('\n')
		md_datas = request.POST['md_datas'].split('\n')
		bpa = request.POST['base_annotations'].split('\n')
		refstruct = secondary_structure.SecondaryStructure(dbn=request.POST['refstruct'])
		messages = []
		structures = []
		mapping_data = []
		base_annotations = []
		for dbn in dbns:
			structures.append(secondary_structure.SecondaryStructure(dbn=dbn))
		for i in range(len(md_seqposes)):
			seqpos = [int(pos) for pos in md_seqposes[i].split(',')]
			data = [float(d) for d in md_datas[i].split(',')]
			mapping_data.append(mapping.MappingData(data=data, seqpos=seqpos))
		for annotations in bpa:
			if len(annotations) > 0:
				try:
					base_annotations.append(str_to_bpdict(annotations)) 
				except ValueError:
					messages.append('An error occurred when annotating helices, please contact tsuname [at] stanford [dot] edu to report this bug')
		if len(request.POST['modifiers']):
			modifiers = request.POST['modifiers'].split(',')
		else:
			modifiers = ['Pseudo energy' for y in sequences]
		panels, ncols, nrows = render_to_varna(sequences, structures, modifiers, titles, mapping_data, base_annotations, refstruct)
		form = VisualizerForm(request.POST)
		return render_to_response('html/predict_result.html', {'panels':panels, 'messages':messages,'ncols':ncols, 'nrows':nrows, 'form':form}, context_instance=RequestContext(request))

