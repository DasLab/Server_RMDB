from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpRequest
# from django.core.servers.basehttp import FileWrapper

from src.models import *

from rdatkit import settings

# from itertools import chain
import simplejson
import sys
import urllib
# import subprocess


def api_rnastr_ver(request):
    ver_rna = os.popen(settings.RNA_STRUCTURE_FOLD + ' -v').readlines()[0].replace('Fold: Version', '').strip()[:-1]
    ver_rdat = settings.VERSION
    ver_py = sys.version[0:6].strip()
    json = {'ver_rna': ver_rna, 'ver_rdat': ver_rdat, 'ver_py': ver_py}
    return HttpResponse(simplejson.dumps(json), content_type='application/json')


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

