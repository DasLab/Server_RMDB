import os
import sys
import time
import traceback
import zipfile

from django.core.management.base import BaseCommand

from src.models import RMDBEntry
from src.settings import *


class Command(BaseCommand):
    help = 'Archives all RDAT files for batch download.'

    def handle(self, *args, **options):
        t0 = time.time()
        self.stdout.write('%s:\t%s' % (time.ctime(), ' '.join(sys.argv)))
        flag = False

        try:
            ### Zip published RDATS for batch download
            entryDict = {}
            zf = zipfile.ZipFile('%s/data/published_rdat.zip' % MEDIA_ROOT, 'w', zipfile.ZIP_DEFLATED)
            
            # Grab each published entry and define the path to the associated RDAT file
            # We don't write the zip file here because we have multiple versions with the same id
            # which is handled by writing the entry rdat dir to a dict keyed by rmdb_id
            entries = RMDBEntry.objects.all().filter(status='PUB')
            for entry in list(entries):
                # If the entry was superceded by another entry, don't include it
                if entry.supercede_by:
                    print(entry.rmdb_id, ' : ', entry.supercede_by)
                    # print("Skipping")
                    # print(entry.rmdb_id)
                    continue        
                entryDict[entry.rmdb_id] = '%s%s' % (PATH.DATA_DIR['FILE_DIR'], entry.rmdb_id)

            # For each entry, get the path to the associated rdat and write to zip file
            for rmdb_id in entryDict:
                rdatPath = '%s/%s.rdat' % (entryDict[rmdb_id], rmdb_id)
                if os.path.exists(rdatPath):
                    zf.write(rdatPath,'%s.rdat' % rmdb_id)
            zf.close()

            ### Zip all RDATS for backup
            all_rdats = [i for i in os.listdir(PATH.DATA_DIR['FILE_DIR']) if (not i.startswith('.') and i != "search")]
            zf = zipfile.ZipFile('%s/data/all_rdat.zip' % MEDIA_ROOT, 'w', zipfile.ZIP_DEFLATED)
            for rdat_name in all_rdats:
                if os.path.exists('%s%s/%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], rdat_name, rdat_name)):
                    zf.write('%s%s/%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], rdat_name, rdat_name), '%s.rdat' % rdat_name)
            zf.close()

        except Exception:
            err = traceback.format_exc()
            print err
            self.stdout.write("    \033[41mERROR\033[0m: Failed to archive all \033[94mRDAT\033[0m files.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_zip.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True

        if flag:
            self.stdout.write("Finished with errors!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
            sys.exit(1)
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: finished archive all \033[94mRDAT\033[0m files.")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))

