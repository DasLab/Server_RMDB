from rmdb.repository.settings import *
from rmdb import settings
from django.core.management  import setup_environ
setup_environ(settings)
from django.template.defaultfilters import slugify
from rmdb.repository.models import *
from rdatkit.datahandlers import RDATFile
import pdb
import sys

mock = False
if '--mock' in sys.argv:
    print 'Mock mode on'
    mock = True

if '-h' in sys.argv:
    print 'sync.db [options]'
    print 'Options:'
    print '--mock      Adds a new version of each entry when performing the rdat sync'
    
for e in RMDBEntry.objects.filter(rmdb_id='ETERNA_R77_0001'):
    print 'Doing ' + e.rmdb_id
    if mock:
	f = open('%s/%s/%s_synced.rdat' % (RDAT_FILE_DIR, e.rmdb_id, e.rmdb_id), 'w')
    else:
	f = open('%s/%s/%s_%s.rdat' % (RDAT_FILE_DIR, e.rmdb_id, e.rmdb_id, e.version), 'w')
    write_annotations = True
    write_comments = True
    f.write('RDAT_VERSION 0.33\n')
    for c in ConstructSection.objects.filter(entry=e):
	f.write('NAME ' + c.name + '\n')
	f.write('SEQUENCE ' + c.sequence + '\n')
	f.write('STRUCTURE ' + c.structure + '\n')
	f.write('OFFSET ' + str(c.offset) + '\n')
	f.write('SEQPOS ' + c.seqpos.strip('[]').replace(',', '\t') + '\n')
	if c.mutpos and c.mutpos.strip():
	    f.write('MUTPOS ' + c.mutpos.strip('[]').replace(',', '\t').replace("'", '') + '\n')
	if c.xsel and c.xsel.strip():
	    f.write('XSEL ' + c.xsel.replace(',', '\t') + '\n')
	if write_annotations:
	    f.write('ANNOTATION ' + '\t'.join(['%s:%s' % (a.name, a.value) for a in EntryAnnotation.objects.filter(section=e)]) + '\n\n')
	    write_annotations = False
	if write_comments:
	    f.write('\n'.join(['COMMENT '+ com for com in e.comments.strip().split('\n')]) + '\n\n')
	    write_comments = False
	    datas = [d for d in DataSection.objects.filter(construct_section=c)]
	    for i, d in enumerate(datas):
		f.write('ANNOTATION_DATA:' + str(i+1) + '\t' + '\t'.join(['%s:%s' % (a.name, a.value.encode('ascii', 'ignore')) for a in DataAnnotation.objects.filter(section=d)]) + '\n')
	    f.write('\n')
	    for i, d in enumerate(datas):
		f.write('REACTIVITY:' + str(i+1) + '\t' + d.values.replace(',', '\t') + '\n')
	    f.write('\n')
	    for i, d in enumerate(datas):
		if d.errors != None and len(d.errors.strip()) > 0:
		    f.write('REACTIVITY_ERROR:' + str(i+1) + '\t' + d.errors.replace(',', '\t') + '\n')
	    f.write('\n')
	    for i, d in enumerate(datas):
		if d.xsel != None and len(d.xsel.strip()) > 0:
		    f.write('XSEL_REFINE:' + str(i+1) + '\t' + d.xsel.replace(',', '\t') + '\n')
	    f.write('\n')

	    for i, d in enumerate(datas):
		if d.trace != None and len(d.trace.strip()) > 0:
		    f.write('TRACE:' + str(i+1) + '\t' + d.trace.replace(',', '\t') + '\n')
	    f.write('\n')
	    for i, d in enumerate(datas):
		if d.seqpos != None and len(d.seqpos.strip()) > 0:
		    f.write('SEQPOS:' + str(i+1) + '\t' + d.seqpos.replace(',', '\t') + '\n')
	    f.write('\n')
    f.close()
    print 'Checking if RDAT file is correct'
    rdat = RDATFile()
    rdat.load(open(f.name))
    print rdat.validate()


	    
