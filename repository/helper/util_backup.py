import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from django.core.management import setup_environ
setup_environ(settings)
from repository.settings import *
from repository.models import *
from repository.helper.helper_display import *

print "#1: Backing up MySQL database..."
os.popen('mysqldump --quick rmdb -u root -pbeckman | gzip > %s/data/mysql_dump.gz' % MEDIA_ROOT)
print "    \033[92mSUCCESS\033[0m: \033[94mMySQL\033[0m database dumped."

print "#2: Backing up RDAT files..."
if os.path.exists('%s/data/rdat_files' % MEDIA_ROOT):
	os.popen('rm -rf %s/data/rdat_files' % MEDIA_ROOT)
os.mkdir('%s/data/rdat_files' % MEDIA_ROOT)
all_rdats =  os.listdir(RDAT_FILE_DIR)
all_rdats = [i for i in os.listdir(RDAT_FILE_DIR) if (i[0] != '.' and i != "search")]
for rdat in all_rdats:
	os.popen('cp %s/data/files/%s/%s.rdat %s/data/rdat_files/%s.rdat' % (MEDIA_ROOT, rdat, rdat, MEDIA_ROOT, rdat))
os.popen('cd %s/data/ && tar zcf rdat_files.tgz rdat_files/*' % MEDIA_ROOT)
os.popen('rm -rf %s/data/rdat_files' % MEDIA_ROOT)
print "    \033[92mSUCCESS\033[0m: \033[41m%s\033[0m \033[94mRDAT\033[0m files archived." % len(all_rdats)

print "#3: Backing up all data files..."
if os.path.exists('%s/data/data_backup' % MEDIA_ROOT):
	os.popen('rm -rf %s/data/data_backup' % MEDIA_ROOT)
os.mkdir('%s/data/data_backup' % MEDIA_ROOT)
os.popen('cp -r %s/data/files %s/data/data_backup/' % (MEDIA_ROOT, MEDIA_ROOT))
os.popen('cp -r %s/data/construct_img %s/data/data_backup/' % (MEDIA_ROOT, MEDIA_ROOT))
os.popen('cp -r %s/data/thumbs %s/data/data_backup/' % (MEDIA_ROOT, MEDIA_ROOT))
os.popen('cd %s/data/ && tar zcf data_backup.tgz data_backup/' % MEDIA_ROOT)
os.popen('rm -rf %s/data/data_backup' % MEDIA_ROOT)
print "    \033[92mSUCCESS\033[0m: all \033[94mdata\033[0m files synced."

print "All done!"
