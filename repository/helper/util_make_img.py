import os
import sys
sys.path.append(os.path.abspath('../../'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "repository.settings") 

from repository.settings import *
from repository.models import *
from repository.helper.helper_display import *
from repository.helper.helper_deposit import *

from rdatkit.datahandlers import RDATFile


def make_images(id):
	construct = ConstructSection.objects.filter(id=id)
	construct.id = id
	entry = RMDBEntry.objects.filter(id=construct.values('entry'))
	entry.type = entry.values('type')[0]['type']
	entry.datacount = entry.values('datacount')[0]['datacount']
	entry.version = entry.values('version')[0]['version']
	rmdb_id = entry.values('rmdb_id')[0]['rmdb_id']

	rdatfile = RDATFile()
	file_name = '%s%s/%s_%s.rdat' %(PATH.DATA_DIR['RDAT_FILE_DIR'], rmdb_id, rmdb_id, entry.version)
	if not os.path.isfile(file_name):
		file_name = '%s%s/%s.rdat' %(PATH.DATA_DIR['RDAT_FILE_DIR'], rmdb_id, rmdb_id)
	rf = open(file_name, 'r')
	rdatfile.load(rf)
	rf.close()
	for k in rdatfile.constructs:
		c = rdatfile.constructs[k]
		generate_images(construct, c, entry.type, engine='matplotlib')
		generate_varna_thumbnails(entry)

	return rmdb_id


if len(sys.argv) > 3:
	print('Usage:')
	print('    %s <c_id> <DEBUG>' % sys.argv[0])
	exit()

DEBUG = False
if len(sys.argv) >= 2:
	if len(sys.argv) > 2 and sys.argv[2] == 'DEBUG':
		DEBUG = True
		all_ids = [int(sys.argv[1])]
	elif sys.argv[1] == 'DEBUG':
		DEBUG = True
		all_ids = [d.values()[0] for d in ConstructSection.objects.values('id').distinct()]
	else:
		all_ids = [int(sys.argv[1])]
else:
	os.popen('rm -rf %s/*' % PATH.DATA_DIR['CONSTRUCT_THMB_DIR'])
	os.popen('rm -rf %s/*' % PATH.DATA_DIR['CONSTRUCT_IMG_DIR'])
	all_ids = [d.values()[0] for d in ConstructSection.objects.values('id').distinct()]


print "\033[92m**\033[0m \033[94mYou should be running\033[0m \033[41m\"ssh -X\"\033[0m\033[94m for image processing (matplotlib windows)!\033[0m"
err_ids = []
for i, id in enumerate(all_ids):
	if DEBUG:
		rmdb_id = make_images(id)
		print "\033[92mSUCCESS\033[0m: ", (i+1), "/", len(all_ids), " : \033[94m#", id, ": ", rmdb_id, "\033[0m"
	else:
		try: 
			rmdb_id = make_images(id)
			print "\033[92mSUCCESS\033[0m: ", (i+1), "/", len(all_ids), " : \033[94m#", id, ": ", rmdb_id, "\033[0m"
		except:
			err_ids.append(id)
			print "\033[41mFAILURE\033[0m: ", (i+1), "/", len(all_ids), " : \033[94m#", id, "\033[0m"

print "All done!"
print "\033[41mError(s)\033[0m encountered:"
print "\033[94m", err_ids, "\033[0m"
