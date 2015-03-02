from rmdb.repository.settings import *
from rmdb import settings
from django.core.management  import setup_environ
setup_environ(settings)
from django.template.defaultfilters import slugify
from rmdb.repository.models import *
import pdb


entries = RMDBEntry.objects.all()
fastafile = open('/home/daslab/rdat/rmdb/external/rmdb_rnabob.fasta', 'w')
for entry in entries:
    print 'Doing %s' % entry.rmdb_id
    csections = ConstructSection.objects.filter(entry=entry)
    for cs in csections:
	fastafile.write('>%s\n' % cs.id)
	fastafile.write('%s\n' % (cs.structure.replace('(', 'G').replace('.', 'A').replace(')', 'C')))
