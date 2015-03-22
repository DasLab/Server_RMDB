import matplotlib
matplotlib.use('Agg')
import pdb
import numpy
import os
from rdatkit import rna, secondary_structure, mapping, view
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "repository.settings") 

from repository.settings import *
from repository.models import *
from repository.views import *

def precalculate_structures(entry):
    try:
	constructs = ConstructSection.objects.filter(entry=entry)
	for c in constructs:
	    datas = DataSection.objects.filter(construct_section=c)
	    for d in datas:
		bonuses = get_correct_mapping_bonuses(d, c)
		for i, b in enumerate(bonuses):
		    if b == -1.0:
			bonuses[i] = -999
		m = mapping.MappingData(data=bonuses)
		structs = secondary_structure.fold(c.sequence, mapping_data=m)
		if len(structs) == 0:
# No non-trivial structures found, try with data normalization
		    m = mapping.MappingData(data=bonuses, norm=True)
		    structs = secondary_structure.fold(c.sequence, mapping_data=m)
                    if len(structs) == 0:
			    d.structure = 'NA'
                    else:
		        d.structure = structs[0].dbn
		else:
		    d.structure = structs[0].dbn
		d.save()
    except ConstructSection.DoesNotExist:
        print 'FATAL! There are no constructs for entry %s' % entry.rmdb_id
	    
   

def upload_file(uploadfile, publication, description, authors, type, pubmed_id, filetype='rdat'):
    filename = uploadfile.name[uploadfile.name.rfind('/')+1:]
    rmdb_id = filename.lower().replace('.rdat','').replace('.xsel','').replace('.isatab','').upper()
    print 'Uploading %s' % rmdb_id
    isatabfile = ISATABFile()
    rdatfile = RDATFile()
    rdatfile.loaded = False
    isatabfile.loaded = False
    rf = open('/tmp/%s'%filename, 'w')
    rf.write(uploadfile.read())
    rf.close()
    rf = open('/tmp/%s'%filename)
    proceed = True
    if filetype == 'isatab':
	isatabfile = ISATABFile()
	try:
	    isatabfile.load(rf.name)
	    isatabfile.loaded = True
	    rdatfile = isatabfile.toRDAT()
	except Exception:
	    print 'Your ISATAB file does not seem to be valid; please check and resubmit'
	    proceed = False
    else:
	try:
	    rdatfile.load(rf)
	    rdatfile.loaded = True
	    isatabfile = rdatfile.toISATAB()
	except Exception as e:
	    print e
	    print 'Your RDAT file does not seem to be valid; please check and resubmit'
	    proceed = False
	if proceed:
	    publication = Publication()
	    publication.title = publication
	    publication.authors = authors
	    publication.pubmed_id = pubmed_id
	    publication.save()
	    datacount = 0
	    constructcount = 0
	    entries = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version')
	    if len(entries) > 0:
		prev_entry = entries[0]
		current_version = prev_entry.version
		owner = prev_entry.owner
	    else:
		current_version = 0
		owner = None
	    if current_version > 0 and False: #owner != request.user:
		print 'RMDB entry %s exists and you cannot update it since you are not the owner' % rmdb_id
	    entry = RMDBEntry()
	    entry.comments = rdatfile.comments
	    entry.publication = publication
	    entry.authors = authors
	    entry.description = description
	    entry.type = type
	    entry.rmdb_id = rmdb_id
	    entry.datacount = 0
	    entry.constructcount = 0
            entry.revision_status = 'PUB'
	    entry.owner = User.objects.get(username='tsuname')
	    entry.version = current_version + 1
	    if current_version == 0:
		entry.latest = True 
	    entry.save()
	    if not os.path.exists('%s%s' % (PATH.DATA_DIR['RDAT_FILE_DIR'], entry.rmdb_id)):
		os.mkdir('%s%s' % (PATH.DATA_DIR['RDAT_FILE_DIR'], entry.rmdb_id))
	    if not os.path.exists('%s%s' % (PATH.DATA_DIR['ISATAB_FILE_DIR'], entry.rmdb_id)):
		os.mkdir('%s%s' % (PATH.DATA_DIR['ISATAB_FILE_DIR'], entry.rmdb_id))
	    rdatname = '%s%s/%s_%s.rdat' % (PATH.DATA_DIR['RDAT_FILE_DIR'], entry.rmdb_id, entry.rmdb_id, entry.version)
	    os.popen('mv /tmp/%s %s' % (filename, rdatname))
	    os.popen('cp %s %s%s/%s.rdat' % (rdatname, PATH.DATA_DIR['RDAT_FILE_DIR'], entry.rmdb_id, entry.rmdb_id))
	    os.popen('cp %s %s%s/%s_synced.rdat' % (rdatname, PATH.DATA_DIR['RDAT_FILE_DIR'], entry.rmdb_id, entry.rmdb_id))
	    # Breaks Excel compatibility if data/columns are > 256
	    if len(rdatfile.values.values()[0]) < 256:
		isatabfile.save('%s%s/%s_%s.xls' % (PATH.DATA_DIR['ISATAB_FILE_DIR'], entry.rmdb_id, entry.rmdb_id, entry.version))
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


if __name__ == '__main__':
    constructs = ConstructSection.objects.all()
    for c in constructs:
	e = RMDBEntry.objects.get(constructsection=c)
	print 'Doing %s' % e.rmdb_id
	precalculate_structures(e)
	#generate_varna_thumbnails(e)
