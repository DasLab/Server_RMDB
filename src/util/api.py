from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
# from django.core.servers.basehttp import FileWrapper

# from src.models import *
from src.util.search import *

# from rdatkit import settings

# from itertools import chain
import simplejson
# import sys
# import subprocess




def search(request, sstring):
    if 'type' in request.GET:
        keyword = request.GET['type']
        return HttpResponse(simplejson.dumps(simple_search(sstring, keyword), sort_keys=True, indent=' ' * 4), content_type='application/json')
    else:
        return HttpResponse(simplejson.dumps(simple_search(sstring, ''), sort_keys=True, indent=' ' * 4), content_type='application/json')
