import simplejson
import sys
import textwrap
import time
import traceback

from django.core.management.base import BaseCommand

from src.settings import *
from src.models import RMDBEntry, ConstructSection


class Command(BaseCommand):
    help = 'Cache RMDB statistics and browse JSON.'

    def get_rmdb_stats(self):
        rmdb_ids = [d.values()[0] for d in RMDBEntry.objects.values('rmdb_id').distinct()]
        N_all = 0
        N_RNA = 0
        # N_RNA = ConstructSection.objects.values('name').distinct().count()
        N_puzzle = 0
        N_eterna = 0
        N_constructs = 0
        N_datapoints = 0
        for rmdb_id in rmdb_ids:
            entries = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version')
            if len(entries) >= 0:
                N_all += 1
                N_RNA += len(entries)

                if 'RNAPZ' in rmdb_id:
                    N_puzzle += 1
                if 'ETERNA' in rmdb_id:
                    N_eterna += 1
                e = entries[0]
            N_datapoints += e.data_count
            N_constructs += e.construct_count       
        return {'N_all': N_all, 'N_RNA': N_RNA, 'N_puzzle': N_puzzle, 'N_eterna': N_eterna, 'N_constructs': N_constructs, 'N_datapoints' : N_datapoints}

    def browse_json_list(self, names_d):
        constructs = []
        for c in names_d:
            entries = RMDBEntry.objects.filter(constructsection__name=c['name']).filter(status='PUB').order_by('rmdb_id', '-version')
            entry_ids = []
            SS_entries, MA_entries, MM_entries, TT_entries = [], [], [], []

            for e in entries:
                if e.rmdb_id not in entry_ids:
                    entry_ids.append(e.rmdb_id)
                    e.cid = ConstructSection.objects.filter(entry = e ).values('id')[0]['id']
                    comment = e.comments.split()
                    for i, m in enumerate(comment):
                        if len(m) > 40:
                            comment[i] = ' '.join(textwrap.wrap(m, 40))
                    entry = {'rmdb_id':e.rmdb_id, 'cid':e.cid, 'version':e.version, 'construct_count':e.construct_count, 'data_count':e.data_count, 'authors':e.authors, 'comments':' '.join(comment), 'title':e.publication.title, 'latest':e.supercede_by}
                    if e.type == "SS":
                        SS_entries.append(entry)
                    elif e.type == "MM":
                        MM_entries.append(entry)
                    elif e.type == "MA":
                        MA_entries.append(entry)
                    elif e.type == "TT":
                        TT_entries.append(entry)

            constructs.append({'name':c['name'], 'SS_entry':SS_entries, 'MM_entry':MM_entries, 'MA_entry':MA_entries, 'TT_entry':TT_entries})
        return constructs
 
    def get_rmdb_category(self, flag):
        if flag == "puzzle":
            names_d = ConstructSection.objects.filter(name__icontains='Puzzle').values('name').distinct()
        elif flag == "eterna":
            names_d = ConstructSection.objects.filter(name__icontains='EteRNA').values('name').distinct()
        else:
            names_d = ConstructSection.objects.exclude(name__icontains='EteRNA').exclude(name__icontains='Puzzle').values('name').distinct()
        names_d = names_d.order_by('name')
        return self.browse_json_list(names_d)


    def handle(self, *args, **options):
        t0 = time.time()
        self.stdout.write('%s:\t%s' % (time.ctime(), ' '.join(sys.argv)))

        flag = False
        try:
            open('%s/cache/stat_stats.json' % MEDIA_ROOT, 'w').write(simplejson.dumps(self.get_rmdb_stats(), indent=' ' * 4, sort_keys=True))

            open('%s/cache/stat_browse_eterna.json' % MEDIA_ROOT, 'w').write(simplejson.dumps(self.get_rmdb_category('eterna'), indent=' ' * 4, sort_keys=True))
            open('%s/cache/stat_browse_puzzle.json' % MEDIA_ROOT, 'w').write(simplejson.dumps(self.get_rmdb_category('puzzle'), indent=' ' * 4, sort_keys=True))
            open('%s/cache/stat_browse_normal.json' % MEDIA_ROOT, 'w').write(simplejson.dumps(self.get_rmdb_category('normal'), indent=' ' * 4, sort_keys=True))

        except Exception:
            self.stdout.write("    \033[41mERROR\033[0m: Failed to cache \033[94mRMDB Entry\033 statistics.")
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

