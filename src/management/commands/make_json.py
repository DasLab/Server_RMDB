import os
import sys
import time
import traceback

from django.core.management.base import BaseCommand
from django.core.management import call_command

from src.settings import *
from src.models import *
from src.util.media import *


class Command(BaseCommand):
    help = 'Makes JSON tags and heatmap files for all RMDBEntry, or a particular one.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('rmdb_id', nargs='*', type=str, help='list of RMDB_IDs, or use ALL')
        parser.add_argument('-A', '--all', action='store_true', dest='is_all', help='Process all RMDB_IDs')

    def handle(self, *args, **options):
        t0 = time.time()
        self.stdout.write('%s:\t%s' % (time.ctime(), ' '.join(sys.argv)))
        flag = False

        if options['is_all']:
            call_command('cleanup')
            all_rdats = [i for i in os.listdir(PATH.DATA_DIR['FILE_DIR']) if (not i.startswith('.') and i != "search")]

            tmp_file = os.listdir(PATH.DATA_DIR['JSON_DIR'])
            for f in tmp_file:
                os.remove(PATH.DATA_DIR['JSON_DIR'] + f)

        elif options['rmdb_id']:
            all_rdats = options['rmdb_id']
        else:
            raise RuntimeError('Use -A or provide any RMDB_IDs.')

        err_rdats = []
        for i, rmdb_id in enumerate(all_rdats):
            try:
                rmdb_id = rmdb_id.upper().strip()
                entry = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-id')
                if len(entry):
                    entry = entry[0]
                else:
                    self.stdout.write("\033[41mERROR\033[0m: RMDBEntry does not exist: \033[94m%s\033[0m" % rmdb_id)

                save_json(rmdb_id)
                self.stdout.write("\033[92mSUCCESS\033[0m: %d / %d : \033[94m%s\033[0m" % (i + 1, len(all_rdats), rmdb_id))
            except Exception:
                err_rdats.append(rmdb_id)
                self.stdout.write("\033[41mFAILURE\033[0m: %d / %d : \033[94m%s\033[0m" % (i + 1, len(all_rdats), rmdb_id))
                err = traceback.format_exc()
                ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
                open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
                open('%s/cache/log_cron_json.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
                flag = True

        if flag:
            self.stdout.write("Finished with errors!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
            self.stdout.write("\033[41mError(s)\033[0m encountered:")
            self.stdout.write("\033[94m%s\033[0m" % str(err_rdats))
            sys.exit(1)
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: tags and heatmap JSON files for \033[94m%s\033[0m generated." % len(all_rdats))
            self.stdout.write("All done successfully!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))

