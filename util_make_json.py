import os
import shutil
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from django.core.management import setup_environ
import settings
setup_environ(settings)
from rmdb.repository.settings import *
from rmdb.repository.models import *
from rmdb.repository.helper_display import *


dept_rdats = 1
while (dept_rdats):
	rmdb_ids = [d.values()[0] for d in RMDBEntry.objects.values('rmdb_id').distinct()]
	all_rdats =  os.listdir(RDAT_FILE_DIR)
	all_rdats = [i for i in os.listdir(RDAT_FILE_DIR) if (i[0] != '.' and i != "search")]

	dept_rdats = [i for i in all_rdats if i not in rmdb_ids]
	for rmdb_id in dept_rdats:
		shutil.rmtree(os.path.join(RDAT_FILE_DIR, rmdb_id))

# all_rdats = ['RNAPZ8_TST_0001']
err_rdats = []

for i, rmdb_id in enumerate(all_rdats):
	try: 
		make_json_for_rdat(rmdb_id)
		print "\033[92mSUCCESS\033[0m: ", (i+1), "/", len(all_rdats), " : \033[94m", rmdb_id, "\033[0m"
	except:
		err_rdats.append(rmdb_id)
		print "\033[41mFAILURE\033[0m: ", (i+1), "/", len(all_rdats), " : \033[94m", rmdb_id, "\033[0m"

print "All done!"
print "\033[41mError(s)\033[0m encountered:"
print "\033[94m", err_rdats, "\033[0m"
