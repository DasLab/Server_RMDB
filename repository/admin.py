from django.contrib import admin
from django.forms import ModelForm, widgets, DateField, DateInput
from django.utils.html import format_html
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from datetime import datetime
from time import sleep, time

from repository.console import *
from repository.cron import *
from repository.models import *
from repository.settings import *


UserAdmin.list_display = ('username', 'email', 'last_login', 'is_active', 'is_staff', 'is_superuser')
UserAdmin.ordering = ('-is_superuser', '-is_staff', 'username')
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class ConstructInLine(admin.StackedInline):
    model = ConstructSection
    extra = 0

class EntryAnnotationInLine(admin.TabularInline):
    model = EntryAnnotation
    extra = 1

class EntryAdmin(admin.ModelAdmin):
    inlines = [EntryAnnotationInLine, ConstructInLine]
    list_display = ('id', 'rmdb_id', 'version', 'short_description', 'revision_status')

class PublicationAdmin(admin.ModelAdmin):
    list_display = ('pubmed_id', 'title', 'authors')

class OrganismAdmin(admin.ModelAdmin):
    list_display = ('taxonomy_id', 'name')

class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('date', 'title')

admin.site.register(RMDBEntry, EntryAdmin)
admin.site.register(NewsItem, NewsItemAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Organism, OrganismAdmin)





def sys_stat(request):
    sys_ver_weekly()
    return HttpResponseRedirect('/admin')
admin.site.register_view('sys_stat', view=sys_stat, visible=False)

def backup_stat(request):
    get_backup_stat()
    return HttpResponseRedirect('/admin/backup')
admin.site.register_view('backup_stat', view=backup_stat, visible=False)

def backup_form(request):
    return HttpResponse(get_backup_form(), content_type='application/json')
admin.site.register_view('backup_form', view=backup_form, visible=False)

def backup_now(request):
    backup_weekly()
    return backup_stat(request)
admin.site.register_view('backup_now', view=backup_now, visible=False)

def upload_now(request):
    gdrive_weekly()
    return backup_stat(request)
admin.site.register_view('upload_now', view=upload_now, visible=False)


def apache_stat(request):
    return HttpResponse(restyle_apache(), content_type='application/json')
admin.site.register_view('apache_stat', view=apache_stat, visible=False)

def apache(request):
    return render_to_response(PATH.HTML_PATH['admin_apache'], {}, context_instance=RequestContext(request))
admin.site.register_view('apache/', view=apache, visible=False)


def aws(request):
    return render_to_response(PATH.HTML_PATH['admin_aws'], {'timezone':TIME_ZONE}, context_instance=RequestContext(request))
admin.site.register_view('aws/', view=aws, visible=False)

def aws_stat(request):
    json = aws_stats(request)
    if isinstance(json, HttpResponseBadRequest): return json
    return HttpResponse(json, content_type='application/json')
admin.site.register_view('aws_stat', view=aws_stat, visible=False)

def aws_admin(request):
    json = ga_stats()
    if isinstance(json, HttpResponseBadRequest): return json
    return HttpResponse(json, content_type='application/json')
admin.site.register_view('aws_admin', view=aws_admin, visible=False)

def ga(request):
    return render_to_response(PATH.HTML_PATH['admin_ga'], {}, context_instance=RequestContext(request))
admin.site.register_view('ga/', view=ga, visible=False)

def ga_admin(request):
    json = ga_stats()
    if isinstance(json, HttpResponseBadRequest): return json
    return HttpResponse(json, content_type='application/json')
admin.site.register_view('ga_admin', view=ga_admin, visible=False)

def git(request):
    return render_to_response(PATH.HTML_PATH['admin_git'], {'timezone':TIME_ZONE}, context_instance=RequestContext(request))
admin.site.register_view('git/', view=git, visible=False)

def git_stat(request):
    json = git_stats(request)
    if isinstance(json, HttpResponseBadRequest):
        return json
    elif isinstance(json, HttpResponseServerError):
        i = 0
        while (isinstance(json, HttpResponseServerError) and i <= 5):
            i += 1
            sleep(1)
            json = git_stats(request)
        if isinstance(json, HttpResponseServerError): return json
    return HttpResponse(json, content_type='application/json')
admin.site.register_view('git_stat', view=git_stat, visible=False)

def ssl_dash(request):
    return HttpResponse(ssl_stats(request), content_type='application/json')
admin.site.register_view('ssl_dash', view=ssl_dash, visible=False)


def backup(request):
    flag = 0
    if request.method == 'POST':
        set_backup_form(request)
        flag = 1

    f = open('%s/config/cron.conf' % MEDIA_ROOT, 'r')
    lines = f.readlines()
    f.close()

    index =  [i for i, line in enumerate(lines) if 'KEEP_BACKUP' in line][0]
    keep = int(lines[index].split(':')[1])
    return render_to_response(PATH.HTML_PATH['admin_backup'], {'form':BackupForm(), 'flag':flag, 'keep':keep, 'email':EMAIL_HOST_USER}, context_instance=RequestContext(request))
admin.site.register_view('backup/', view=backup, visible=False)

def dir(request):
    return render_to_response(PATH.HTML_PATH['admin_dir'], {}, context_instance=RequestContext(request))
admin.site.register_view('dir/', view=dir, visible=False)

def doc(request):
    return render_to_response(PATH.HTML_PATH['admin_doc'], {}, context_instance=RequestContext(request))
admin.site.register_view('doc/', view=doc, visible=False)


def get_ver(request):
    f = open('%s/cache/stat_sys.txt' % MEDIA_ROOT, 'r')
    lines = f.readlines()
    f.close()
    lines = ''.join(lines)
    return HttpResponse(lines, content_type='text/plain')
admin.site.register_view('get_ver/', view=get_ver, visible=False)

def get_backup(request):
    f = open('%s/cache/stat_backup.txt' % MEDIA_ROOT, 'r')
    lines = f.readlines()
    f.close()
    lines = ''.join(lines)
    return HttpResponse(lines, content_type='text/plain')
admin.site.register_view('get_backup/', view=get_backup, visible=False)

