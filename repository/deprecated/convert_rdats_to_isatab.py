import rmdb.settings
from django.core.management  import setup_environ
setup_environ(rmdb.settings)
from rmdb.repository.models import *
from rdatkit.datahandlers import ISATABFile, RDATFile
from settings import *


for entry in RMDBEntry.objects.all():
    rdatpath = RDAT_FILE_DIR + entry.rmdb_id + '/'
    isatabpath = ISATAB_FILE_DIR + entry.rmdb_id + '/'
    print 'Doing ' + entry.rmdb_id
    for f in os.listdir(rdatpath):
	rdat = RDATFile()
	rdat.load(open(rdatpath + f))
	isatab = rdat.toISATAB()
	if not os.path.exists(isatabpath):
	    os.mkdir(isatabpath)
	isatab.save(isatabpath + f.replace('rdat', 'xls'))
	  
