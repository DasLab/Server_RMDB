import os
import sys
import time
import traceback

from django.core.management.base import BaseCommand
from django.core.management import call_command

from rdatkit.datahandlers import RDATFile

from src.settings import *
from src.models import *
from src.util.media import *


class Command(BaseCommand):
    help = 'Makes images and thumbnail files for all RMDBEntry, or a particular one.\n\033[92m**\033[0m \033[94mYou should be running\033[0m \033[41m\"ssh -X\"\033[0m\033[94m for image processing (matplotlib windows)!\033[0m'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('rmdb_id', nargs='*', type=str, help='list of RMDB_IDs, or use ALL')
        parser.add_argument('-A', '--all', action='store_true', dest='is_all', help='Process all RMDB_IDs')

    def handle(self, *args, **options):
        t0 = time.time()
        self.stdout.write('%s:\t%s' % (time.ctime(), ' '.join(sys.argv)))

        flag = False
        t = time.time()

        if options['is_all']:
            call_command('cleanup')
            all_rdats = os.listdir(PATH.DATA_DIR['FILE_DIR'])
            all_rdats = [i for i in os.listdir(PATH.DATA_DIR['FILE_DIR']) if (i[0] != '.' and i != "search")]

            tmp_file = os.listdir(PATH.DATA_DIR['IMG_DIR'])
            for f in tmp_file:
                os.remove(PATH.DATA_DIR['IMG_DIR'] + f)
            tmp_file = os.listdir(PATH.DATA_DIR['THUMB_DIR'])
            for f in tmp_file:
                os.remove(PATH.DATA_DIR['THUMB_DIR'] + f)

        elif options['rmdb_id']:
            all_rdats = options['rmdb_id']
        else:
            raise RuntimeError('Use -A or provide any RMDB_IDs.')

        err_rdats = []
        for i, rmdb_id in enumerate(all_rdats):
            try:
                file_name = '%s%s/%s.rdat' % (PATH.DATA_DIR['FILE_DIR'], rmdb_id, rmdb_id)
                rdatfile = RDATFile()
                rdatfile.load(open(file_name, 'r'))

                entry = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-id')[0]
                construct = ConstructSection.objects.get(entry_id=entry.id)

                for k in rdatfile.constructs:
                    c = rdatfile.constructs[k]
                    save_image(rmdb_id, construct, c, entry.type)
                save_thumb(entry)
                self.stdout.write("\033[92mSUCCESS\033[0m: %d / %d : \033[94m%s\033[0m" % (i + 1, len(all_rdats), rmdb_id))
            except Exception:
                err_rdats.append(rmdb_id)
                self.stdout.write("\033[41mFAILURE\033[0m: %d / %d : \033[94m%s\033[0m" % (i + 1, len(all_rdats), rmdb_id))
                err = traceback.format_exc()
                print err
                ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
                open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
                open('%s/cache/log_cron_img.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
                flag = True

        if flag:
            self.stdout.write("Finished with errors!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
            self.stdout.write("\033[41mError(s)\033[0m encountered:")
            self.stdout.write("\033[94m%s\033[0m" % str(err_rdats))
            sys.exit(1)
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: iamges and thumbnail files for \033[94m%s\033[0m generated." % len(all_rdats))
            self.stdout.write("All done successfully!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))

