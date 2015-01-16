from rmdb.repository.models import *


def get_rmdb_stats():
	rmdb_ids = [d.values()[0] for d in RMDBEntry.objects.values('rmdb_id').distinct()]
	N_all = 0
	N_RNA = 0
	# N_RNA = ConstructSection.objects.values('name').distinct().count()
	N_puzzle = 0
	N_eterna = 0
	N_constructs = 0
	N_datapoints = 0
	# visited_entries = []
	for rmdb_id in rmdb_ids:
		entries = RMDBEntry.objects.filter(rmdb_id=rmdb_id).order_by('-version')
		# print rmdb_id
		if len(entries) >= 0:
			N_all += 1
			N_RNA += len(entries)

			if 'RNAPZ' in rmdb_id:
				N_puzzle += 1
			if 'ETERNA' in rmdb_id:
				N_eterna += 1
			# print [e for e in entries]
			e = entries[0]
		N_datapoints += e.datacount
		N_constructs += e.constructcount
		
		# if e.rmdb_id[:5] not in visited_entries:
		# N_datapoints += e.datacount
		# N_constructs += e.constructcount
		# visited_entries.append(e.rmdb_id[:5])
	return (N_all, N_RNA, N_puzzle, N_eterna, N_constructs, N_datapoints)


class BrowseResults:
	pass


def get_rmdb_category(flag):
	if flag == "puzzle":
		names_d = ConstructSection.objects.filter(name__icontains='Puzzle').values('name').distinct()
	elif flag =="eterna":
		names_d = ConstructSection.objects.filter(name__icontains='EteRNA').values('name').distinct()
	else:
		names_d = ConstructSection.objects.exclude(name__icontains='EteRNA').exclude(name__icontains='Puzzle').values('name').distinct()

	names_d = names_d.order_by( 'name' )    
	constructs = [BrowseResults() for i in range(len(names_d))]

	for i, c in enumerate(names_d):
		constructs[i].name = c['name']
		entries = RMDBEntry.objects.filter(constructsection__name=c['name']).filter(revision_status='PUB').order_by( 'rmdb_id', '-version' )
		constructs[i].entries = []
		entry_ids = []
		for e in entries:
			if e.rmdb_id not in entry_ids:
				entry_ids.append(e.rmdb_id)
				e.cid = ConstructSection.objects.filter( entry = e ).values( 'id' )[ 0 ][ 'id' ]
				constructs[i].entries.append(e)

	return constructs


