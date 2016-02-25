import datetime
import subprocess
import sys
import time
import traceback

from django.core.management.base import BaseCommand

from src.settings import *
from src.console import get_date_time, get_backup_stat, send_notify_emails


class Command(BaseCommand):
    help = 'Uploads MySQL database, static files, Apache2 settings and config settings from local backup/ folder to Google Drive, and deletes expired backup files in Google Drive. Uploaded files will be named with date.'

    def handle(self, *args, **options):
        t0 = time.time()
        self.stdout.write('%s:\t%s' % (time.ctime(), ' '.join(sys.argv)))

        d = time.strftime('%Y%m%d') #datetime.datetime.now().strftime('%Y%m%d')
        gdrive_dir = 'echo'
        if not DEBUG: gdrive_dir = 'cd %s' % APACHE_ROOT
        prefix = ''
        if DEBUG: prefix = '_DEBUG'

        flag = False
        t = time.time()
        self.stdout.write("#1: Uploading MySQL database...")
        try:
            subprocess.check_call('%s && drive upload -f %s/backup/backup_mysql.tgz -t %s_%s_mysql%s.tgz' % (gdrive_dir, MEDIA_ROOT, env('SERVER_NAME'), d, prefix), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to upload \033[94mMySQL\033[0m database.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_gdrive.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mMySQL\033[0m database uploaded.")
        self.stdout.write("Time elapsed: %.1f s." % (time.time() - t))

        t = time.time()
        self.stdout.write("#2: Uploading static files...")
        try:
            subprocess.check_call('%s && drive upload -f %s/backup/backup_static.tgz -t %s_%s_static%s.tgz' % (gdrive_dir, MEDIA_ROOT, env('SERVER_NAME'), d, prefix), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to upload \033[94mstatic\033[0m files.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_gdrive.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mstatic\033[0m files uploaded.")
        self.stdout.write("Time elapsed: %.1f s." % (time.time() - t))

        t = time.time()
        self.stdout.write("#3: Uploading apache2 settings...")
        try:
            subprocess.check_call('%s && drive upload -f %s/backup/backup_apache.tgz -t %s_%s_apache%s.tgz' % (gdrive_dir, MEDIA_ROOT, env('SERVER_NAME'), d, prefix), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to upload \033[94mapache2\033[0m settings.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_gdrive.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mapache2\033[0m settings uploaded.")
        self.stdout.write("Time elapsed: %.1f s." % (time.time() - t))

        t = time.time()
        self.stdout.write("#4: Uploading config settings...")
        try:
            subprocess.check_call('%s && drive upload -f %s/backup/backup_config.tgz -t %s_%s_config%s.tgz' % (gdrive_dir, MEDIA_ROOT, env('SERVER_NAME'), d, prefix), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to upload \033[94mconfig\033[0m settings.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_gdrive.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True
        else:
            self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94mconfig\033[0m settings uploaded.")
        self.stdout.write("Time elapsed: %.1f s." % (time.time() - t))


        t = time.time()
        self.stdout.write("#5: Removing obsolete backups...")
        try:
            old = (datetime.date.today() - datetime.timedelta(days=KEEP_BACKUP)).strftime('%Y-%m-%dT00:00:00')
            list_mysql = subprocess.Popen("%s && drive list -q \"title contains '%s_' and (title contains '_mysql.tgz' or title contains '_mysql_DEBUG.tgz') and modifiedDate <= '%s'\"| awk '{printf $1\" \"}'" % (gdrive_dir, env('SERVER_NAME'), old), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[1:]
            list_static = subprocess.Popen("%s && drive list -q \"title contains '%s_' and (title contains '_static.tgz' or title contains '_static_DEBUG.tgz') and modifiedDate <= '%s'\"| awk '{ printf $1\" \"}'" % (gdrive_dir, env('SERVER_NAME'), old), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[1:]
            list_apache = subprocess.Popen("%s && drive list -q \"title contains '%s_' and (title contains '_apache.tgz' or title contains '_apache_DEBUG.tgz') and modifiedDate <= '%s'\"| awk '{ printf $1\" \"}'" % (gdrive_dir, env('SERVER_NAME'), old), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[1:]
            list_config = subprocess.Popen("%s && drive list -q \"title contains '%s_' and (title contains '_config.tgz' or title contains '_config_DEBUG.tgz') and modifiedDate <= '%s'\"| awk '{ printf $1\" \"}'" % (gdrive_dir, env('SERVER_NAME'), old), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[1:]
            list_all = list_mysql + list_static + list_apache + list_config
        except:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to check obsolete \033[94mbackup\033[0m files.")
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_gdrive.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True

        for id in list_all:
            try:
                subprocess.check_call('%s && drive info -i %s' % (gdrive_dir, id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                subprocess.check_call('%s && drive delete -i %s' % (gdrive_dir, id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                self.stdout.write("    \033[41mERROR\033[0m: Failed to remove obsolete \033[94mbackup\033[0m files.")
                err = traceback.format_exc()
                ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
                open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
                open('%s/cache/log_cron_gdrive.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
                flag = True

        if not flag: self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94m%s\033[0m obsolete backup files removed." % len(list_all))
        self.stdout.write("Time elapsed: %.1f s.\n" % (time.time() - t))

        if flag:
            self.stdout.write("Finished with errors!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
            sys.exit(1)
        else:
            if DEBUG:
                self.stdout.write("\033[94m Uploaded to Google Drive. \033[0m")
            else:
                (t_cron, d_cron, t_now) = get_date_time('gdrive')
                gdrive_dir = 'echo'
                if not DEBUG: gdrive_dir = 'cd %s' % APACHE_ROOT
                gdrive_list = subprocess.Popen("%s && drive list -q \"title contains '%s_'\"" % (gdrive_dir, env('SERVER_NAME')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0].strip().split()[4:]
                html = 'File\t\t\t\tTime\t\t\t\tSize\n\n'
                for i in range(0, len(gdrive_list), 6):
                    html += '%s\t\t%s %s\t\t%s %s\n' % (gdrive_list[i+1], gdrive_list[i+4], gdrive_list[i+5], gdrive_list[i+2], gdrive_list[i+3])
                send_notify_emails('{%s} SYSTEM: Weekly Sync Notice' % env('SERVER_NAME'), 'This is an automatic email notification for the success of scheduled weekly sync of the %s Server backup contents to Google Drive account.\n\nThe crontab job is scheduled at %s (UTC) on every %sday.\n\nThe last system backup was performed at %s (PDT).\n\n%s\n\n%s Admin\n' % (env('SERVER_NAME'), t_cron, d_cron, t_now, html, env('SERVER_NAME')))
                self.stdout.write("Admin email (Weekly Sync Notice) sent.")
            get_backup_stat()
            self.stdout.write("Admin Backup Statistics refreshed.")

            self.stdout.write("All done successfully!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
