from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# from django.core.servers.basehttp import FileWrapper

from src.env import error400, error403, error404, error500
from src.settings import env
# from src.models import *
from src.util.search import *

# from rdatkit import settings

# from itertools import chain
import hmac
from hashlib import sha1
import simplejson
# import sys
# import subprocess


def search(request, sstring):
    sstring = sstring.encode('ascii', 'ignore')
    if 'type' in request.GET:
        keyword = request.GET.get('type')
        return HttpResponse(simplejson.dumps(simple_search(sstring, keyword), sort_keys=True, indent=' ' * 4), content_type='application/json')
    else:
        return HttpResponse(simplejson.dumps(simple_search(sstring, ''), sort_keys=True, indent=' ' * 4), content_type='application/json')


@csrf_exempt
def git_hook(request):
    if request.method != 'POST': return error404(request)
    if ('HTTP_X_HUB_SIGNATURE' not in request.META) or ('HTTP_X_GITHUB_DELIVERY' not in request.META) or ('HTTP_X_GITHUB_EVENT' not in request.META): return error400(request)

    signature = request.META['HTTP_X_HUB_SIGNATURE']
    json = request.body
    mac = hmac.new(env('GITHOOK_SECRET'), msg=json, digestmod=sha1)
    if not hmac.compare_digest('sha1=' + str(mac.hexdigest()), str(signature)): return error403(request)
    json = simplejson.loads(json)

    try:
        call_command('dist', repo=[json['repository']['full_name']])
    except Exception:
        return error500(request)
    return HttpResponse(content="", status=201)

