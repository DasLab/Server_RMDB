from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from models import *
from rdatkit.datahandlers import RDATFile
from settings import *
from django import forms

def home( request ):
    return HttpResponseRedirect('/repository/')
