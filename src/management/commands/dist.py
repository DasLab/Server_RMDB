import os
import simplejson
import subprocess
import sys
import time
import traceback
import zipfile

from django.core.management.base import BaseCommand

from github import Github

from src.settings import *


class Command(BaseCommand):
    help = 'Retrieves all code releases from Github as zip archives.'

    def handle(self, *args, **options):
        t0 = time.time()
        self.stdout.write('%s:\t%s' % (time.ctime(), ' '.join(sys.argv)))

        flag = False
        dist_names = [('DasLab/map_seeker', 'map_seeker', 'MAPSeeker'), ('DasLab/reeffit', 'reeffit', 'REEFFIT'), ('hitrace/rdatkit', 'rdatkit', 'RDATKit'), ('hitrace/hitrace', 'hitrace', 'HiTRACE'), ('DasLab/Biers', 'Biers', 'Biers')]
        try:
            gh = Github(login_or_token=GIT["ACCESS_TOKEN"])
            json = {}

            for dist in dist_names:
                repo = dist[0]
                releases = gh.get_repo(repo).get_releases()
                result = []
                for rel in releases:
                    ver = rel.tag_name
                    ver_trim = ver.replace('v', '') if ver.startswith('v') else ver
                    if not os.path.exists('%s/dist/%s-%s.zip' % (MEDIA_ROOT, dist[2], ver_trim)):
                        subprocess.check_call('cd %s/dist && curl -O -J -L -u %s:%s https://github.com/%s/archive/%s.zip' % (MEDIA_ROOT, GIT["USERNAME"], GIT["PASSWORD"], repo, ver), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        subprocess.check_call('cd %s/dist && mv %s-%s.zip temp.zip && mv temp.zip %s-%s.zip' % (MEDIA_ROOT, dist[1], ver_trim, dist[2], ver_trim), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        print "Release \033[94m%s\033[0m downloaded." % ver_trim
                    else:
                        print "Release \033[94m%s\033[0m already exists and is ignored." % ver_trim

                    result.append({'version': ver_trim, 'title': rel.title, 'description': rel.body})
                json[dist[2].lower()] = result

                ver = 'master'
                if os.path.exists('%s/dist/%s-master.zip' % (MEDIA_ROOT, dist[2])):
                    os.remove('%s/dist/%s-master.zip' % (MEDIA_ROOT, dist[2]))
                subprocess.check_call('cd %s/dist && curl -O -J -L -u %s:%s https://github.com/%s/archive/master.zip' % (MEDIA_ROOT, GIT["USERNAME"], GIT["PASSWORD"], repo), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                subprocess.check_call('cd %s/dist && mv %s-master.zip temp.zip && mv temp.zip %s-master.zip' % (MEDIA_ROOT, dist[1], dist[2]), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                print "Release \033[94mlatest master\033[0m downloaded."
                zf = zipfile.ZipFile('%s/dist/%s-master.zip' % (MEDIA_ROOT, dist[2]), 'r')
                data = zf.read('%s-master/LICENSE.md' % dist[1])
                open('%s/dist/%s-LICENSE.md' % (MEDIA_ROOT, dist[2]), 'w').write(data)

            simplejson.dump(json, open('%s/cache/stat_dist.json' % MEDIA_ROOT, 'w'), indent=' ' * 4, sort_keys=True)
            
        except Exception:
            err = traceback.format_exc()
            self.stdout.write("    \033[41mERROR\033[0m: Failed to download \033[92m%s\033[0m release \033[94m%s\033[0m." % (repo, ver))
            err = traceback.format_exc()
            ts = '%s\t\t%s\n' % (time.ctime(), ' '.join(sys.argv))
            open('%s/cache/log_alert_admin.log' % MEDIA_ROOT, 'a').write(ts)
            open('%s/cache/log_cron_dist.log' % MEDIA_ROOT, 'a').write('%s\n%s\n' % (ts, err))
            flag = True

        if flag:
            self.stdout.write("Finished with errors!")
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))
            sys.exit(1)
        else:
            for dist in dist_names:
                self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94m%s\033[0m releases downloaded." % dist[0])
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))

