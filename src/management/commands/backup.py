import os
#import shutil
import subprocess
import sys
import tarfile
import time
import traceback

from django.core.management.base import BaseCommand

from src.settings import *
from src.console import get_date_time, get_backup_stat, send_notify_emails


class Command(BaseCommand):
    help = 'Backups MySQL database, static files, Apache2 settings and config settings to local backup/ folder. Existing backup files will be overwritten.'

    def handle(self, *args, **options):
        t0 = time.time()
        self.stdout.write('%s:\t%s' % (time.ctime(), ' '.join(sys.argv)))

        flag = False
        t = time.time()
        self.stdout.write("#1: Backing up MySQL database...")
        try:
            subprocess.check_call('mysqldump --quick %s -u %s -p%s > %s/backup/backup_mysql' % (env.db()['NAME'], env.db()['USER'], env.db()['PASSWORD'], MEDIA_ROOT), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            tarfile.open('%s/backup/backup_mysql.tgz' % MEDIA_ROOT, 'w:gz').add('%s/backup/backup_mysql' % MEDIA_ROOT, arcname='backup_mysql')
            os.remove('%s/backup/backup_mysql' % MEDIA_ROOT)
        except:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to dump \033[94mMySQL\033[0m database.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_backup.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mMySQL\033[0m database dumped.")
        self.stdout.write("Time elapsed: %.1f s." % (time.time() - t))


        t = time.time()
        self.stdout.write("#2: Backing up static files...")
        try:
            tarfile.open('%s/backup/backup_static.tgz' % MEDIA_ROOT, 'w:gz').add('%s/data' % MEDIA_ROOT, arcname='data')
        except:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to archive \033[94mstatic\033[0m files.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_backup.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mstatic\033[0m files synced.")
        self.stdout.write("Time elapsed: %.1f s." % (time.time() - t))


        t = time.time()
        self.stdout.write("#3: Backing up apache2 settings...")
        try:
            pass
            # tarfile.open('%s/backup/backup_apache2.tgz' % MEDIA_ROOT, 'w:gz').add('/etc/apache2', arcname='apache2')
        except:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to archive \033[94mapache2\033[0m settings.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_backup.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mapache2\033[0m settings saved.")
        self.stdout.write("Time elapsed: %.1f s." % (time.time() - t))


        t = time.time()
        self.stdout.write("#4: Backing up config settings...")
        try:
            tarfile.open('%s/backup/backup_config.tgz' % MEDIA_ROOT, 'w:gz').add('%s/config' % MEDIA_ROOT, arcname='config')
        except:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to archive \033[94mconfig\033[0m settings.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_backup.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mconfig\033[0m settings saved.")
        self.stdout.write("Time elapsed: %.1f s.\n" % (time.time() - t))

        if flag:
            self.stdout.write("Finished with errors!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
            sys.exit(1)
        else:
            if DEBUG:
                self.stdout.write("\033[94m Backed up locally. \033[0m")
            else:
                (t_cron, d_cron, t_now) = get_date_time('backup')
                local_list = subprocess.Popen('ls -gh %s/backup/*.*gz' % MEDIA_ROOT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()
                html = 'File\t\t\t\tTime\t\t\t\tSize\n\n'
                for i in range(0, len(local_list), 8):
                    html += '%s\t\t%s %s, %s\t\t%s\n' % (local_list[i+7], local_list[i+4], local_list[i+5], local_list[i+6], local_list[i+3])
                send_notify_emails('{%s} SYSTEM: Weekly Backup Notice' % env('SERVER_NAME'), 'This is an automatic email notification for the success of scheduled weekly backup of the %s Server database and static contents.\n\nThe crontab job is scheduled at %s (UTC) on every %sday.\n\nThe last system backup was performed at %s (PDT).\n\n%s\n\n%s Admin\n' % (env('SERVER_NAME'), t_cron, d_cron, t_now, html, env('SERVER_NAME')))
                self.stdout.write("Admin email (Weekly Backup Notice) sent.")
            get_backup_stat()
            self.stdout.write("Admin Backup Statistics refreshed.")

            self.stdout.write("All done successfully!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))

