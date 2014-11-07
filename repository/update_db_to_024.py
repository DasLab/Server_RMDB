from rmdb.repository.settings import *
from rmdb import settings
from django.core.management  import setup_environ
setup_environ(settings)
from django.template.defaultfilters import slugify
from rmdb.repository.models import *
import pdb


def invert(sarr):
    narr = sarr.split(',')[::-1]
    return ','.join(narr)
     
entries = RMDBEntry.objects.all()
for entry in entries:
    print 'Doing %s' % entry.rmdb_id
    pdb.set_trace()
    csections = ConstructSection.objects.filter(entry=entry)
    for cs in csections:
	nseqpos = cs.seqpos.strip('[]').split(',')[::-1]
	nmutpos = cs.mutpos.strip('[]').split(',')[::-1]
	cs.seqpos = ','.join(nseqpos)
	cs.mutpos = ','.join(nmutpos)
	datas = DataSection.objects.filter(construct_section=cs)
	for d in datas:
	    if d.xsel:
		d.xsel = invert(d.xsel)
	    if d.values:
		d.values = invert(d.values)
	    if d.errors:
		d.errors = invert(d.errors)
	    if d.trace:
		d.trace = invert(d.trace)
	    if d.seqpos:
		d.seqpos = invert(d.seqpos)
	    d.save()
	cs.save()



