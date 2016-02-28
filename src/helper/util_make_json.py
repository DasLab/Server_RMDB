import os
import shutil
import sys
import traceback

from django.core.wsgi import get_wsgi_application
sys.path.append(os.path.abspath('../../'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings") 
application = get_wsgi_application()

from src.settings import *
from src.models import *
from src.helper.helper_display import *


if len(sys.argv) > 3:
	print('Usage:')
	print('    %s <rmdb_id> <DEBUG>' % sys.argv[0])
	exit()

dept_rdats = 1
DEBUG = False
while (dept_rdats):
	rmdb_ids = [d.values()[0] for d in RMDBEntry.objects.values('rmdb_id').distinct()]
	all_rdats =  os.listdir(PATH.DATA_DIR['RDAT_FILE_DIR'])
	all_rdats = [i for i in os.listdir(PATH.DATA_DIR['RDAT_FILE_DIR']) if (i[0] != '.' and i != "search")]

	dept_rdats = [i for i in all_rdats if i not in rmdb_ids]
	for rmdb_id in dept_rdats:
		shutil.rmtree(os.path.join(PATH.DATA_DIR['RDAT_FILE_DIR'], rmdb_id))

if len(sys.argv) >= 2:
	if len(sys.argv) > 2 and sys.argv[2] == 'DEBUG':
		DEBUG = True
	all_rdats = [sys.argv[1]]
	if not os.path.exists(os.path.join(PATH.DATA_DIR['RDAT_FILE_DIR'], all_rdats[0])):
		print "\033[41mError\033[0m: rmdb_id invalid, no data files folder found. Abort."
		exit()


err_rdats = []
for i, rmdb_id in enumerate(all_rdats):
	if DEBUG:
		make_json_for_rdat(rmdb_id)
		print "\033[92mSUCCESS\033[0m: ", (i+1), "/", len(all_rdats), " : \033[94m", rmdb_id, "\033[0m"
	else:
		try: 
			make_json_for_rdat(rmdb_id)
			print "\033[92mSUCCESS\033[0m: ", (i+1), "/", len(all_rdats), " : \033[94m", rmdb_id, "\033[0m"
		except:
			print traceback.format_exc()
			err_rdats.append(rmdb_id)
			print "\033[41mFAILURE\033[0m: ", (i+1), "/", len(all_rdats), " : \033[94m", rmdb_id, "\033[0m"

print "All done!"
print "\033[41mError(s)\033[0m encountered:"
print "\033[94m", err_rdats, "\033[0m"
