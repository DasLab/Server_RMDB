from rmdb.repository.settings import *
from rmdb import settings
from django.core.management  import setup_environ
setup_environ(settings)
from django.template.defaultfilters import slugify
from rmdb.repository.models import *

pdbs = {}

pdbs['5SRRNA'] = '3OFC,3OAS,3ORB,2WWQ'
pdbs['ADDRSW'] = '1Y26,1Y27,2G9C,3GO2'
pdbs['CIDGMP'] = '3MXH,3IWN,3MUV,3MUT'
pdbs['GLYCFN'] = '3P49'
pdbs['TRP4P6'] = '1GID,1L8V,1HR2,2R8S'
pdbs['TRNAPH'] = '1L0U,1EHZ'

entries = RMDBEntry.objects.all()

for e in entries:
    for pdbid in pdbs:
	if pdbid  in e.rmdb_id:
	    e.pdb_entries = pdbs[pdbid]
	    e.save()
	    break


