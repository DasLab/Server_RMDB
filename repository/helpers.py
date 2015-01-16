import matplotlib
matplotlib.use('Agg')
import pdb
import numpy
import os
from rmdb.repository.settings import *
from rdatkit import secondary_structure, mapping
from rmdb import settings
from django.core.management  import setup_environ
setup_environ(settings)
from rmdb.repository.models import *
from rmdb.repository.views import *


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
