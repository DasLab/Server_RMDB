from rmdb.repository.models import *
from rmdb.settings import *

import glob
import time


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


def get_history():
	file_list = glob.glob(MEDIA_ROOT + "/design/code/log_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].txt")
	log_content = []

	for log_file in file_list:
		f = open(log_file, 'r')
		lines = [line for line in f.readlines() if line.strip()]
		f.close()

		ls_1_flag = 0
		ls_2_flag = 0
		for i in range(len(lines)):
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
		date_string = log_file[log_file.find("log_")+4 :-4]
		date_string = time.strftime("%b %d, %Y (%a)", time.strptime(date_string, "%Y%m%d"))
		lines.insert(0, "<i>%s</i><br/>" % date_string)
		log_content.insert(0, "".join(lines))

	return log_content
