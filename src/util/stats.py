import textwrap
from django.db.models import Max

from src.models import *


def parse_history():
    hist_list = []
    hist = HistoryItem.objects.all()
    for h in hist:
        lines = h.content
        lines = [line for line in lines.split('\n') if line.strip()]
        ls_1_flag = 0
        ls_2_flag = 0
        for i in xrange(len(lines)):
            lines[i] = lines[i].rstrip()
            if lines[i][0] == "#":
                lines[i] = "<span class=\"lead\"><b>" + lines[i][1:] + "</b></span><br/>"
            elif lines[i][0] != '-':
                if lines[i][0] == "!":
                    lines[i] = "by <kbd><i>" + lines[i][1:] + "</i></kbd><br/><br/>"
                else:
                    lines[i] = "<p>" + lines[i] + "</p><p><ul>"

            else:
                if lines[i][:2] != '-\\':
                    lines[i] = "<li><u>" + lines[i][1:] + "</u></li>"
                    if ls_1_flag:
                        lines[i] = "</ul></p>" + lines[i]
                    ls_1_flag = i

                else:
                    lines[i] = "<li>" + lines[i][2:] + "</li>"
                    if ls_2_flag < ls_1_flag:
                        lines[i] = "<ul><p>" + lines[i]
                    ls_2_flag = i
        lines.append("</ul></ul><br/><hr/>")
        date_string = h.date.strftime("%b %d, %Y (%a)")
        lines.insert(0, "<i>%s</i><br/>" % date_string)
        hist_list.insert(0, ''.join(lines))

    return hist_list


def get_rmdb_stats():
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
    return {'N_all': N_all, 'N_RNA': N_RNA, 'N_puzzle': N_puzzle, 'N_eterna': N_eterna, 'N_constructs': N_constructs, 'N_datapoints': N_datapoints}


def browse_json_list(names_d):
    constructs = []
    for c in names_d:
        entries = RMDBEntry.objects.filter(constructsection__name=c['name']).filter(status='PUB').order_by('rmdb_id', '-version')
        entry_ids = []
        (SS_entries, TT_entries, MA_entries, MM_entries, MR_entries) = ([], [], [], [], [])

        for e in entries:
            if e.rmdb_id not in entry_ids:
                entry_ids.append(e.rmdb_id)
                comment = e.comments.split()
                for i, m in enumerate(comment):
                    if len(m) > 40:
                        comment[i] = ' '.join(textwrap.wrap(m, 40))
                entry = {'rmdb_id': e.rmdb_id, 'version': e.version, 'construct_count': e.construct_count, 'data_count': e.data_count, 'authors': e.authors, 'comments': ' '.join(comment), 'title': e.publication.title, 'latest': e.supercede_by}
                if e.type == "SS" or e.type == "DC":
                    SS_entries.append(entry)
                elif e.type == "TT":
                    TT_entries.append(entry)
                elif e.type == "MM":
                    MM_entries.append(entry)
                elif e.type == "MR":
                    MR_entries.append(entry)
                elif e.type == "MA":
                    MA_entries.append(entry)

        constructs.append({'name': c['name'], 'SS_entry': SS_entries, 'TT_entry': TT_entries, 'MM_entry': MM_entries, 'MA_entry': MA_entries, 'MR_entry': MR_entries})
    return constructs


def get_rmdb_category(flag):
    latest_versions = RMDBEntry.objects.values('rmdb_id').annotate(latest_version=Max('version'))
    q_statement = Q()
    for pair in latest_versions:
        q_statement |= (Q(entry__rmdb_id=pair['rmdb_id']) & Q(entry__version=pair['latest_version']))

    LatestConstructSec = ConstructSection.objects.filter(q_statement)

    if flag == "puzzle":
        names_d = LatestConstructSec.filter(name__icontains='Puzzle').values('name').distinct()
    elif flag == "eterna":
        names_d = LatestConstructSec.filter(name__icontains='EteRNA').values('name').distinct()
    else:
        names_d = LatestConstructSec.exclude(name__icontains='EteRNA').exclude(name__icontains='Puzzle').values('name').distinct()
    names_d = names_d.order_by('name')
    return browse_json_list(names_d)

