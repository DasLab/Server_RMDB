import shutil
import simplejson
import sys
import time
import traceback

from django.core.management.base import BaseCommand

from src.settings import *
from src.util.stats import *


class Command(BaseCommand):
    help = 'Cache RMDB statistics and browse JSON.'

    def handle(self, *args, **options):
        t0 = time.time()
        self.stdout.write('%s:\t%s' % (time.ctime(), ' '.join(sys.argv)))

        flag = False
        try:
            simplejson.dump(get_rmdb_stats(), open('%s/cache/stat_stats_tmp.json' % MEDIA_ROOT, 'w'), indent=' ' * 4, sort_keys=True)
            simplejson.dump(get_rmdb_category('eterna'), open('%s/cache/stat_browse_eterna_tmp.json' % MEDIA_ROOT, 'w'), indent=' ' * 4, sort_keys=True)
            simplejson.dump(get_rmdb_category('puzzle'), open('%s/cache/stat_browse_puzzle_tmp.json' % MEDIA_ROOT, 'w'), indent=' ' * 4, sort_keys=True)
            simplejson.dump(get_rmdb_category('general'), open('%s/cache/stat_browse_general_tmp.json' % MEDIA_ROOT, 'w'), indent=' ' * 4, sort_keys=True)

            shutil.move('%s/cache/stat_stats_tmp.json' % MEDIA_ROOT, '%s/cache/stat_stats.json' % MEDIA_ROOT)
            shutil.move('%s/cache/stat_browse_eterna_tmp.json' % MEDIA_ROOT, '%s/cache/stat_browse_eterna.json' % MEDIA_ROOT)
            shutil.move('%s/cache/stat_browse_puzzle_tmp.json' % MEDIA_ROOT, '%s/cache/stat_browse_puzzle.json' % MEDIA_ROOT)
            shutil.move('%s/cache/stat_browse_general_tmp.json' % MEDIA_ROOT, '%s/cache/stat_browse_general.json' % MEDIA_ROOT)

        except Exception:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to cache \033[94mRMDB Entry\033[0m statistics.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_stats.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True

        if flag:
            self.stdout.write("Finished with errors!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
            sys.exit(1)
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mRMDB Entry\033[0m statistics cached.")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))

