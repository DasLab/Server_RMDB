from src.models import *

from itertools import chain
import textwrap
# import time


def simple_search(sstring, keyword):
    if keyword == 'eterna':
        entry_all = RMDBEntry.objects.filter(rmdb_id__startswith='ETERNA').filter(status='PUB').filter(constructsection__datasection__dataannotation__value__icontains=sstring).order_by('rmdb_id', '-version')
    else:
        filtered = RMDBEntry.objects.exclude(rmdb_id__startswith='ETERNA').filter(status='PUB') if (keyword == 'general') else RMDBEntry.objects.filter(status='PUB')

        entry_by_name = filtered.filter(constructsection__name__icontains=sstring).order_by('rmdb_id', '-version')
        entry_by_id = filtered.filter(rmdb_id__icontains=sstring).order_by('rmdb_id', '-version')
        entry_by_comment = filtered.filter(comments__icontains=sstring).order_by('rmdb_id', '-version')
        entry_by_desp = filtered.filter(description__icontains=sstring).order_by('rmdb_id', '-version')
        entry_by_data_anno = filtered.filter(constructsection__datasection__dataannotation__value__icontains=sstring).order_by('rmdb_id', '-version')
        entry_by_anno = filtered.filter(entryannotation__value__icontains=sstring).order_by('rmdb_id', '-version')

        entry_all = list(chain(entry_by_name, entry_by_id, entry_by_desp, entry_by_data_anno, entry_by_anno, entry_by_comment))


    entry_ids = []
    entries = []
    for e in entry_all:
        if e.rmdb_id not in entry_ids:
            e.constructs = ConstructSection.objects.filter(entry=e).values('name').distinct()
            e.cid = ConstructSection.objects.get(entry=e).id

            comment = e.comments.split()
            for i, m in enumerate(comment):
                if len(m) > 40:
                    comment[i] = ' '.join(textwrap.wrap(m, 40))
            entry = {'name': e.constructs[0]['name'], 'rmdb_id': e.rmdb_id, 'cid': e.cid, 'version': e.version, 'construct_count': e.construct_count, 'data_count': e.data_count, 'authors': e.authors, 'comments': ' '.join(comment), 'title': e.publication.title, 'latest': e.supercede_by}

            entry_ids.append(e.rmdb_id)
            entries.append(entry)

    return entries

