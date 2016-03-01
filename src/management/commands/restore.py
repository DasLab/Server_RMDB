import os
import shutil
import subprocess
import sys
import tarfile
import time
import traceback

from django.core.management.base import BaseCommand

from src.settings import *


class Command(BaseCommand):
    help = 'Restores MySQL database, static files, Apache2 settings and config settings from local backup/ folder.'

    def handle(self, *args, **options):
        t0 = time.time()
        self.stdout.write('%s:\t%s' % (time.ctime(), ' '.join(sys.argv)))

        flag = False
        t = time.time()
        self.stdout.write("#1: Restoring MySQL database...")
        try:
            tarfile.open('%s/backup/backup_mysql.tgz' % MEDIA_ROOT, 'r:gz').extractall()
            subprocess.check_call('cat %s/backup/backup_mysql | mysql -u %s -p%s %s' % (MEDIA_ROOT, env.db()['USER'], env.db()['PASSWORD'], env.db()['NAME']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            os.remove('%s/backup/backup_mysql' % MEDIA_ROOT)
        except Exception:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to overwrite \033[94mMySQL\033[0m database.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_restore.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mMySQL\033[0m database overwritten.")
        self.stdout.write("Time elapsed: %.1f s." % (time.time() - t))


        t = time.time()
        self.stdout.write("#2: Restoring static files...")
        try:
            shutil.rmtree('%s/backup/data' % MEDIA_ROOT)
            tarfile.open('%s/backup/backup_static.tgz' % MEDIA_ROOT, 'r:gz').extractall()
            shutil.rmtree('%s/data' % MEDIA_ROOT)
            shutil.move('%s/backup/data' % MEDIA_ROOT, '%s' % MEDIA_ROOT)
            shutil.rmtree('%s/backup/data' % MEDIA_ROOT)
            if not DEBUG:
                subprocess.check_call('%s/util_chmod.sh' % MEDIA_ROOT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except Exception:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to restore \033[94mstatic\033[0m files.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_restore.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mstatic\033[0m files overwritten.")
        self.stdout.write("Time elapsed: %.1f s." % (time.time() - t))


        t = time.time()
        self.stdout.write("#3: Restoring apache2 settings...")
        try:
            shutil.rmtree('%s/backup/apache2' % MEDIA_ROOT)
            tarfile.open('%s/backup/backup_apache.tgz' % MEDIA_ROOT, 'r:gz').extractall()
            shutil.rmtree('/etc/apache2')
            shutil.move('%s/backup/apache2' % MEDIA_ROOT, '/etc/apache2')
            shutil.rmtree('%s/backup/apache2' % MEDIA_ROOT)
            if not DEBUG:
                subprocess.check_call('apache2ctl restart', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except Exception:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to restore \033[94mapache2\033[0m settings.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_restore.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mapache2\033[0m settings overwritten.")
        self.stdout.write("Time elapsed: %.1f s.\n" % (time.time() - t))


        t = time.time()
        self.stdout.write("#4: Restoring config settings...")
        try:
            shutil.rmtree('%s/backup/config' % MEDIA_ROOT)
            tarfile.open('%s/backup/backup_config.tgz' % MEDIA_ROOT, 'r:gz').extractall()
            shutil.rmtree('%s/config' % MEDIA_ROOT)
            shutil.move('%s/backup/config' % MEDIA_ROOT, '%s/config' % MEDIA_ROOT)
            shutil.rmtree('%s/backup/config' % MEDIA_ROOT)
            if not DEBUG:
                subprocess.check_call('apache2ctl restart', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except Exception:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to restore \033[94mconfig\033[0m settings.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_restore.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mconfig\033[0m settings overwritten.")
        self.stdout.write("Time elapsed: %.1f s.\n" % (time.time() - t))


        if flag:
            self.stdout.write("Finished with errors!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
            sys.exit(1)
        else:
            self.stdout.write("All done successfully!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
