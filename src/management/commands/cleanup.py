import os
import shutil
import sys
import time
import traceback

from django.core.management.base import BaseCommand

from src.settings import *
from src.models import *


class Command(BaseCommand):
    help = 'Cleans up old job results from database and folders.'

    def handle(self, *args, **options):
        t0 = time.time()
        self.stdout.write('%s:\t%s' % (time.ctime(), ' '.join(sys.argv)))

        flag = False
        self.stdout.write("Cleaning up obsolete RMDB_IDs...")

        try:
            rmdb_ids = [d.values()[0] for d in RMDBEntry.objects.values('rmdb_id').distinct()]
            all_rdats = [i for i in os.listdir(PATH.DATA_DIR['FILE_DIR']) if (not i.startswith('.') and i != "search")]
            dept_rdats = filter(lambda x: (x not in rmdb_ids), all_rdats)
            for rmdb_id in dept_rdats:
                shutil.rmtree(os.path.join(PATH.DATA_DIR['FILE_DIR'], rmdb_id))

            tmp_file = os.listdir(PATH.DATA_DIR['TMP_DIR'])
            for f in tmp_file:
                os.remove(PATH.DATA_DIR['TMP_DIR'] + f)

        except Exception:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to remove RMDB_ID \033[94m%s\033[0m." % rmdb_id)
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_cleanup.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True

        if flag:
            self.stdout.write("Finished with errors!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
            sys.exit(1)
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94m%s\033[0m obsolete RMDBEntry directories removed." % len(dept_rdats))
            self.stdout.write("All done successfully!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
