from rdatkit.datahandlers import RDATFile
from helpers import *
from rmdb import settings
from django.core.management  import setup_environ
setup_environ(settings)
from rmdb.repository.models import *
from rmdb.repository.settings import *

constructs = ConstructSection.objects.filter(entry__rmdb_id__icontains='R87_0003')
"""
for e in RMDBEntry.objects.all():
    if 'R88' in e.rmdb_id:
	print 'Doing %s' % e.rmdb_id
	generate_varna_thumbnails(e)
"""
for c in constructs:
    e = RMDBEntry.objects.get(constructsection=c)
    print 'Doing %s' % e.rmdb_id
    rdat = RDATFile()
    fname = '%s/%s/%s.rdat' % (RDAT_FILE_DIR, e.rmdb_id, e.rmdb_id) 
    rdat.load(open(fname))
    generate_images(c, rdat.constructs.values()[0], e.type)
    generate_varna_thumbnails(e)
