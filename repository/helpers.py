import matplotlib
matplotlib.use('Agg')
import pdb
import numpy
import os
from rmdb.repository.settings import *
from rdatkit.view import VARNA
from rdatkit import secondary_structure, mapping
from rmdb import settings
from django.core.management  import setup_environ
setup_environ(settings)
from django.template.defaultfilters import slugify
from rmdb.repository.models import *
from rmdb.repository.views import *

def save_annotations(dictionary, section, cl):
    count = 0
    for d in dictionary:
	for value in dictionary[d]:
	    a = cl()
	    a.name = d.strip()
	    if d.strip() == 'mutation':
		count += 1
	    a.value = value
	    a.section = section
	    a.save()
    return count

def get_correct_mapping_bonuses(data, construct):
    vals = [float(x) for x in data.values.split(',')]
    seqpos = [int(x) - construct.offset - 1 for x in construct.seqpos.strip('[]').split(',')]
    bonuses = [-0.1]*len(construct.sequence)
    valmean = sum(vals)/len(vals)
    for i, s in enumerate(seqpos):
        if vals[i] < -0.01:
            bonuses[s] = valmean
        else:
	    bonuses[s] = vals[i]
    return bonuses

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
	    
   

def generate_varna_thumbnails(entry):
    try:
        constructs = ConstructSection.objects.filter(entry=entry)
	for c in constructs:
	    path = '%s%s' % (CONSTRUCT_THMB_DIR, c.id)
	    fname = '%s/%s' % (path, slugify(c.name))
	    datas = DataSection.objects.filter(construct_section=c)
	    if not os.path.exists(path):
		os.mkdir(path)
                os.system('chmod 777 %s' % path)
            if not c.structure or '(' not in c.structure or entry.type == 'MM' or len(datas) > 100:
		peakfname = '%s%s/values.png' % (CONSTRUCT_IMG_DIR, c.id) 
		os.popen('cp %s %s.png' % (peakfname, fname))
		os.popen('convert %s.png %s.gif' % (fname, fname))
                height = min(len(datas), 1000)
                width = 200
	    else:
                height = 200
                width = 200
		os.popen('rm %s/*.png' % path)
		for i, data in enumerate(datas[:5]):
		    bonuses = get_correct_mapping_bonuses(data, c)
		    cms = VARNA.get_colorMapStyle(bonuses)
		    VARNA.cmd(' '*len(c.sequence), c.structure, '%s_%s.png' % (fname, i), options={'colorMapStyle':cms, 'colorMap':bonuses, 'bpStyle':'simple', 'baseInner':'#FFFFFF', 'periodNum':400} )
		print path
                os.popen('convert -delay 100 -resize 300x300 infile.jpg -background none -gravity center -extent 300x300 -loop 0 %s/*.png %s.gif' % (path, fname))
	    os.popen('mogrify -format gif -thumbnail %sx%s! %s.gif' % (width, height, fname))
    except ConstructSection.DoesNotExist:
        print 'FATAL! There are no constructs for entry %s' % entry.rmdb_id

def generate_images(construct_model, construct_section, entry_type, engine='matplotlib'):
    data = DataSection.objects.filter(construct_section=construct_model)
    values = []
    traces = []
    reads = []
    xsels = []
    errors = []
    for d in data:
	values.append([float(x) for x in d.values.strip().split(',')])
	if d.trace:
	    traces.append([float(x) for x in d.trace.strip().split(',')])
	if d.reads:
	    reads.append([float(x) for x in d.reads.strip().split(',')])
	if d.errors:
	    errors.append([float(x) for x in d.errors.strip().split(',')])
	if d.xsel:
	    xsels.append([int(x) for x in d.xsel.strip().split(',')])
    values_array, trace_array, reads_array, xsel_array, errors_array = array(values), array(traces), array(reads), array(xsels), array(errors)
    dir = CONSTRUCT_IMG_DIR+'%s/'%construct_model.id
    if not os.path.exists(dir):
	os.mkdir(dir)
	os.system('chmod 777 %s' % dir)
    values_array, trace_array, reads_array, xsel_array, errors_array = get_arrays(construct_section.data)
    values_dims = shape(values_array)
    trace_dims = shape(trace_array)
    values_mean = values_array.mean(axis=-1)
    values_std = values_array.std(axis=0)
    if entry_type == 'MM':
	order = []
	order_offset = 0
	for i, data in enumerate(construct_section.data):
	    if 'mutation' in data.annotations:
		if data.annotations['mutation'][0].upper() == 'WT':
		    order.append(order_offset)
		    order_offset += 1
		else:
		    order.append(int(data.annotations['mutation'][0].replace('Lib1-','').replace('Lib2-', '')[1:-1]))
	    else:
		order.append(i)
	order = [i[0] for i in sorted(enumerate(order), key=lambda x:x[1])][::-1]
    else:
	order = range(values_dims[0])
    if engine == 'matplotlib':
        has_traces = False
	if size(trace_array) > 0:
	    figure(2)
	    aspect_ratio = "auto"
	    if (entry_type == 'MM'):  aspect_ratio = shape( trace_array[order, :] )[1] / float( shape( trace_array)[0]  )
	    #imshow(trace_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=trace_array.mean(), aspect=aspect_ratio, interpolation='nearest')
	    imshow(trace_array[order, :], cmap=get_cmap('Greys'))
	    #apply_xlabels( construct_section )
	    xticks( [],[] )
	    #apply_ylabels( construct_section )
	    savefig(dir+'/trace.png')
	    has_traces = True
	if size(reads_array) > 0:
	    figure(2)
	    aspect_ratio = "auto"
	    if (entry_type == 'MM'):  aspect_ratio = shape( reads_array[order, :] )[1] / float( shape(reads_array)[0]  )
	    #imshow(trace_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=trace_array.mean(), aspect=aspect_ratio, interpolation='nearest')
	    imshow(reads_array[order, :], cmap=get_cmap('Greys'))
	    #apply_xlabels( construct_section )
	    xticks( [],[] )
	    #apply_ylabels( construct_section )
	    savefig(dir+'/trace.png')
	    has_traces = True


	figure(2)
	clf()

	aspect_ratio = "auto"
	if (entry_type == 'MM'):  aspect_ratio = "equal" #aspect_ratio = shape(values_array)[0]/ float( shape( values_array )[1] )

	imshow(values_array[order, :], cmap=get_cmap('Greys'), vmin=0, vmax=values_array.mean(), aspect=aspect_ratio, interpolation='nearest')


        frame = gca()
	frame.axes.get_xaxis().set_visible(False)
	frame.axes.get_yaxis().set_visible(False)
	#apply_xlabels( construct_section )
	#apply_ylabels( construct_section )
	ylim( [-0.5, shape( values_array )[0]-0.5  ] )
	savefig(dir+'/values.png')

	#figure(1)
	#clf()
	#matshow(corrcoef(values_array.T)**10)
	#savefig(dir+'/corrcoef.png')
	if entry_type == 'SS' and values_dims[0] < 100:
	    for j in range(values_dims[0]):
		figure(1)
		clf()
		bar(range(values_dims[1]), values_array[j,:], yerr=errors_array[j,:])
		bartitle = '  '.join( [','.join(x) if type(x) == list else str(x) for x in construct_section.data[j].annotations.values()] )
		suptitle( bartitle )
		apply_xlabels( construct_section )
		xlim( [0, shape( values_array )[1] ] )
		savefig(dir+'/barplot%s.png'%j)

    return has_traces



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
	    if not os.path.exists('%s%s' % (RDAT_FILE_DIR, entry.rmdb_id)):
		os.mkdir('%s%s' % (RDAT_FILE_DIR, entry.rmdb_id))
	    if not os.path.exists('%s%s' % (ISATAB_FILE_DIR, entry.rmdb_id)):
		os.mkdir('%s%s' % (ISATAB_FILE_DIR, entry.rmdb_id))
	    rdatname = '%s%s/%s_%s.rdat' % (RDAT_FILE_DIR, entry.rmdb_id, entry.rmdb_id, entry.version)
	    os.popen('mv /tmp/%s %s' % (filename, rdatname))
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



if __name__ == '__main__':
    constructs = ConstructSection.objects.all()
    for c in constructs:
	e = RMDBEntry.objects.get(constructsection=c)
	print 'Doing %s' % e.rmdb_id
	precalculate_structures(e)
	#generate_varna_thumbnails(e)
