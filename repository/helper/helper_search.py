from repository.models import *

from itertools import chain
import textwrap


def simple_search_list(sstring, keyword):

	if keyword == 'eterna':
		entry_by_name = RMDBEntry.objects.filter(rmdb_id__startswith='ETERNA').filter(constructsection__name__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
		entry_by_id = RMDBEntry.objects.filter(rmdb_id__startswith='ETERNA').filter(rmdb_id__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
		entry_by_comment = RMDBEntry.objects.filter(rmdb_id__startswith='ETERNA').filter(comments__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
		entry_by_desp = RMDBEntry.objects.filter(rmdb_id__startswith='ETERNA').filter(description__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
		entry_by_data_anno = RMDBEntry.objects.filter(rmdb_id__startswith='ETERNA').filter(constructsection__datasection__dataannotation__value__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
		entry_by_anno = RMDBEntry.objects.filter(rmdb_id__startswith='ETERNA').filter(entryannotation__value__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
	else:
		entry_by_name = RMDBEntry.objects.exclude(rmdb_id__startswith='ETERNA').filter(constructsection__name__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
		entry_by_id = RMDBEntry.objects.exclude(rmdb_id__startswith='ETERNA').filter(rmdb_id__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
		entry_by_comment = RMDBEntry.objects.exclude(rmdb_id__startswith='ETERNA').filter(comments__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
		entry_by_desp = RMDBEntry.objects.exclude(rmdb_id__startswith='ETERNA').filter(description__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
		entry_by_data_anno = RMDBEntry.objects.exclude(rmdb_id__startswith='ETERNA').filter(constructsection__datasection__dataannotation__value__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
		entry_by_anno = RMDBEntry.objects.exclude(rmdb_id__startswith='ETERNA').filter(entryannotation__value__icontains=sstring).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )

	entry_all = list(chain(entry_by_name, entry_by_id, entry_by_desp, entry_by_data_anno, entry_by_anno, entry_by_comment))	


	entry_ids = []
	entries = []
	for e in entry_all:
		if e.rmdb_id not in entry_ids:
			e.constructs = ConstructSection.objects.filter(entry=e).values('name').distinct()
			e.cid = ConstructSection.objects.filter(entry=e).values( 'id' )[ 0 ][ 'id' ]

			comment = e.comments.split()
			for i, m in enumerate(comment):
				if len(m) > 40:
					comment[i] = ' '.join(textwrap.wrap(m, 40))
			entry = {'name':e.constructs[0]['name'], 'rmdb_id':e.rmdb_id, 'cid':e.cid, 'version':e.version, 'construct_count':e.constructcount, 'data_count':e.datacount, 'authors':e.authors, 'comments':' '.join(comment), 'title':e.publication.title, 'latest':e.latest}

			entry_ids.append(e.rmdb_id)
			entries.append(entry)

	return entries

