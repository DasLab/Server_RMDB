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


DIST_NAMES_STD = ['ribokit/MAPseeker', 'ribokit/REEFFIT', 'ribokit/Biers', 'ribokit/RDATKit', 'ribokit/HiTRACE']

class Command(BaseCommand):
    help = 'Retrieves all code releases from Github as zip archives.'

    def add_arguments(self, parser):
        parser.add_argument('--repo', nargs='+', type=str, help="List of repositories, choose from ('" + "', '".join(DIST_NAMES_STD) + "').")


    def handle(self, *args, **options):
        t0 = time.time()
        self.stdout.write('%s:\t%s' % (time.ctime(), ' '.join(sys.argv)))

        flag = False
        if options['repo']:
            dist_names = []
            repos = [repo.lower() for repo in options['repo']]
            for repo in DIST_NAMES_STD:
                if repo.lower() in repos:
                    dist_names.append(repo)
        else:
            dist_names = DIST_NAMES_STD

        try:
            gh = Github(login_or_token=GIT["ACCESS_TOKEN"])
            json = simplejson.load(open('%s/cache/stat_dist.json' % MEDIA_ROOT, 'r'))

            for repo in dist_names:
                dist = repo.split('/')[-1]
                releases = gh.get_repo(repo).get_releases()
                result = []
                for rel in releases:
                    ver = rel.tag_name
                    ver_trim = ver.replace('v', '') if ver.startswith('v') else ver
                    if not os.path.exists('%s/dist/%s-%s.zip' % (MEDIA_ROOT, dist, ver_trim)):
                        subprocess.check_call('cd %s/dist && curl -J -L -H "Authorization: token %s" -o %s/dist/%s-%s.zip https://api.github.com/repos/%s/zipball/%s' % (MEDIA_ROOT, GIT["ACCESS_TOKEN"], MEDIA_ROOT, dist, ver, repo, ver), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        print "Release \033[94m%s\033[0m downloaded." % ver_trim
                    else:
                        print "Release \033[94m%s\033[0m already exists and is ignored." % ver_trim

                    result.append({'version': ver_trim, 'title': rel.title, 'description': rel.body})
                json[dist.lower()] = result

                ver = 'master'
                if os.path.exists('%s/dist/%s-master.zip' % (MEDIA_ROOT, dist)):
                    os.remove('%s/dist/%s-master.zip' % (MEDIA_ROOT, dist))
                subprocess.check_call('cd %s/dist && curl -J -L -H "Authorization: token %s" -o %s/dist/%s-master.zip https://api.github.com/repos/%s/zipball/master' % (MEDIA_ROOT, GIT["ACCESS_TOKEN"], MEDIA_ROOT, dist, repo), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                print "Release \033[94mlatest master\033[0m downloaded."
                zf = zipfile.ZipFile('%s/dist/%s-master.zip' % (MEDIA_ROOT, dist), 'r')
                license = [name for name in zf.namelist() if 'LICENSE.md' in name]
                data = zf.read(license[0])
                open('%s/dist/%s-LICENSE.md' % (MEDIA_ROOT, dist), 'w').write(data)

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
            for repo in dist_names:
                self.stdout.write("    \033[92mSUCCESS\033[0m: \033[94m%s\033[0m releases downloaded." % repo)
            self.stdout.write("Time elapsed: %.1f s." % (time.time() - t0))

