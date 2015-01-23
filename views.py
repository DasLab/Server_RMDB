from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django import forms

from rdatkit.datahandlers import RDATFile

# from models import *
from settings import *

def home( request ):
    return HttpResponseRedirect('/repository/')
