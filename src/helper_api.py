from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpRequest
from django.core.servers.basehttp import FileWrapper

from repository.models import *
from src.helper_stats import *
from src.helper_search import *

# from itertools import chain
import simplejson
# import subprocess


def format_number_comma(x):
	if type(x) not in [type(0), type(0L)]:
		raise TypeError("Parameter must be an integer.")
	if x < 0:
		return '-' + intWithCommas(-x)
	result = ''
	while x >= 1000:
		x, r = divmod(x, 1000)
		result = ",%03d%s" % (r, result)
	return "%d%s" % (x, result)


def api_stats(request):
	(N_all, N_RNA, N_puzzle, N_eterna, N_constructs, N_datapoints) = get_rmdb_stats()
	json = {'N_all':format_number_comma( N_all), 'N_RNA':format_number_comma(N_RNA), 'N_puzzle':format_number_comma(N_puzzle), 'N_eterna':format_number_comma(N_eterna), 'N_constructs':format_number_comma(N_constructs), 'N_datapoints':format_number_comma(N_datapoints)}
	return HttpResponse(simplejson.dumps(json), content_type='application/json')


def api_latest(request):
	entries = RMDBEntry.objects.all().order_by('-creation_date')
	entries_list = set()
	for e in entries:
		entries_list.add(e.rmdb_id)
		if len(entries_list) == 10:
			break
	entries = []
	for e in entries_list:
		entries.append(RMDBEntry.objects.filter(rmdb_id=e).order_by('-creation_date')[0])

	entries_list = []
	for e in entries[::-1]:
		cid = ConstructSection.objects.filter(entry=e).values( 'id' )[ 0 ][ 'id' ]
		rmdb_id = e.rmdb_id
		for c in ConstructSection.objects.filter(entry=e).values('name').distinct():
			name = c['name']
		e_temp = {'cid':cid, 'name':name, 'rmdb_id':rmdb_id}
		entries_list.append(e_temp)
	return HttpResponse(simplejson.dumps(entries_list), content_type='application/json')


def api_news(request):
	news = NewsItem.objects.all().order_by('-date')[:10]
	json = {}
	for i, n in enumerate(news):
		json[i] = {'title':n.title, 'date':n.date.strftime('%b %d, %Y')}
	return HttpResponse(simplejson.dumps(json), content_type='application/json')


def api_history(request):
	return HttpResponse(get_history())


def api_browse(request, keyword):
	constructs = get_rmdb_category(keyword)
	return HttpResponse(simplejson.dumps(constructs), content_type='application/json')


def api_search(request, keyword, sstring):
	sstring = sstring.replace('_', ' ').strip()
	return HttpResponse(simplejson.dumps(simple_search_list(sstring, keyword)), content_type='application/json')


def api_redirect(request, path):
	path = path.rstrip('/')
	html = "<html><header><meta http-equiv=\"refresh\" content=\"0;url=/site_data/files/%s\"/></header></html>" % path
	return HttpResponse(html)







def get_constructs_by_ids():
	constructs = [cdict.values()[0] for cdict in ConstructSection.objects.values('name').distinct()]
	return constructs


def encode_entry(entry):
	entry.annotations = EntryAnnotation.objects.filter(section=entry)
	entry.constructs = ConstructSection.objects.filter(entry=entry)
	for c in entry.constructs:
		c.datas = DataSection.objects.filter(construct_section=c)
		for d in c.datas:
			d.annotations = DataAnnotation.objects.filter(section=d)
	return RMDBJSONEncoder().default(entry)


def api_fetch_entry(request, rmdb_id):
	try:
		entry = RMDBEntry.objects.get(rmdb_id=rmdb_id, latest=True)
	except RMDBEntry.DoesNotExist:
		return HttpResponse('null', mimetype='application/json')
	jsonstr = simplejson.dumps(encode_entry(entry))
	print jsonstr
	return HttpResponse(jsonstr, content_type='application/json')


def api_all_entries(request):
	jsonres = '[' + ','.join([simplejson.dumps(encode_entry(entry)) for entry in RMDBEntry.objects.filter(latest=True)]) + ']'
	return HttpResponse(jsonres, content_type='application/json')


def api_entries_by_organism(request, organism_id):
	jsonres = '[' + ','.join([simplejson.dumps(encode_entry(entry)) for entry in RMDBEntry.objects.filter(organism__taxonomy_id=organism_id, latest=True)]) + ']'
	return HttpResponse(jsonres, content_type='application/json')


def api_entries_by_system(request, system_id):
	constructs = get_constructs_by_ids()
	try:
		id = int(system_id)
	except ValueError:
		return HttpResponse('[]')
	if id < 0 or id >= len(constructs):
		return HttpResponse('[]')
	jsonres = '[' + ','.join([simplejson.dumps(encode_entry(entry)) for entry in RMDBEntry.objects.filter(constructsection__name=constructs[id], latest=True)]) + ']'
	return HttpResponse(jsonres, content_type='application/json')


def api_rmdb_ids_by_organism(request, organism_id):
	jsonres = '[' + ','.join([entry.rmdb_id for entry in RMDBEntry.objects.filter(organism__taxonomy_id=organism_id, latest=True)]) + ']'
	return HttpResponse(jsonres, content_type='application/json')


def api_rmdb_ids_by_system(request, system_id):
	constructs = get_constructs_by_ids()
	try:
		id = int(system_id)
	except ValueError:
		return HttpResponse('[]')
	if id < 0 or id >= len(constructs):
		return HttpResponse('[]')
	jsonres = '[' + ','.join([entry.rmdb_id for entry in RMDBEntry.objects.filter(constructsection__name=constructs[id], latest=True)]) + ']'
	return HttpResponse(jsonres, content_type='application/json')


def api_all_rmdb_ids(request):    
	jsonres = '[' + ','.join(['"' + entry.rmdb_id + '"' for entry in RMDBEntry.objects.filter(latest=True)]) + ']'
	return HttpResponse(jsonres, content_type='application/json')


def api_all_organisms(request):
	jsonres = '[' + ','.join([simplejson.dumps(RMDBJSONEncoder().default(o)) for o in Organism.objects.all()]) + ']'
	return HttpResponse(jsonres, content_type='application/json')


def api_all_systems(request):
	constructs = get_constructs_by_ids()
	jsonres = '[' + ','.join([simplejson.dumps({'id':i, 'name':n}) for i, n in enumerate(constructs)]) + ']'
	return HttpResponse(jsonres, content_type='application/json')
