from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.management import call_command

from src.console import *
from src.models import *
from src.settings import *


UserAdmin.list_display = ('username', 'email', 'last_login', 'is_active', 'is_staff', 'is_superuser')
UserAdmin.ordering = ('-is_superuser', '-is_staff', 'username')
# admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class ConstructInLine(admin.StackedInline):
    model = ConstructSection
    extra = 0

class EntryAnnotationInLine(admin.TabularInline):
    model = EntryAnnotation
    extra = 1

class EntryAdmin(admin.ModelAdmin):
    inlines = [EntryAnnotationInLine, ConstructInLine]
    list_display = ('id', 'rmdb_id', 'version', 'status', 'type', 'short_desp', 'data_count', 'construct_count', 'owner')
    ordering = ('-id',)
    fieldsets = [
        (format_html('<span class="glyphicon glyphicon-book"></span>&nbsp;Entry Basics'),
         {'fields': ['rmdb_id', ('status', 'version', 'supercede_by'), ('owner', 'type'), 'co_owners', 'authors', 'publication', 'description', 'comments', ('is_trace', 'is_eterna'), ('data_count', 'construct_count'), ('organism', 'pdb')]}),
    ]
    search_fields = ['rmdb_id']

class PublicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'pubmed_id', 'authors', 'title')
    ordering = ('-id',)
    fieldsets = [
        (format_html('<span class="glyphicon glyphicon-book"></span>&nbsp;Citation'), {'fields': ['pubmed_id', 'authors', 'title']}),
    ]

class OrganismAdmin(admin.ModelAdmin):
    list_display = ('id', 'tax_id', 'name')
    ordering = ('-tax_id',)
    fieldsets = [
        (format_html('<span class="glyphicon glyphicon-credit-card"></span>&nbsp;Profile'), {'fields': ['tax_id', 'name']}),
    ]

class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('date', 'content')
    ordering = ('-date',)
    fieldsets = [
        (format_html('<span class="glyphicon glyphicon-comment"></span>&nbsp;Contents'), {'fields': ['date', 'content']}),
    ]

class HistoryItemAdmin(admin.ModelAdmin):
    list_display = ('date', 'content')
    ordering = ('-date',)
    fieldsets = [
        (format_html('<span class="glyphicon glyphicon-comment"></span>&nbsp;Contents'), {'fields': ['date', 'content']}),
    ]


class RMDBUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'affiliation', 'last_date')
    ordering = ('-id',)
    fieldsets = [
        (format_html('<span class="glyphicon glyphicon-user"></span>&nbsp;Personal Information'), {'fields': ['user', 'principal_investigator', 'institution', 'department']}),
        (format_html('<span class="glyphicon glyphicon-dashboard"></span>&nbsp;Personal Statistics'), {'fields': ['entry_count', ('data_count', 'construct_count'), ('last_entry', 'last_date')]})
    ]
    search_fields = ['user__username']


class SourceDownloaderAdmin(admin.ModelAdmin):
    list_display = ('date', 'rmdb_user', 'package')
    ordering = ('-date', 'rmdb_user',)

    fieldsets = [
        (format_html('<span class="glyphicon glyphicon-user"></span>&nbsp;Personal Information'), {'fields': ['date', 'rmdb_user', 'package']}),
    ]


admin.site.register(RMDBEntry, EntryAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Organism, OrganismAdmin)
admin.site.register(NewsItem, NewsItemAdmin)
admin.site.register(HistoryItem, HistoryItemAdmin)
admin.site.register(RMDBUser, RMDBUserAdmin)
admin.site.register(SourceDownloader, SourceDownloaderAdmin)


############################################################################################################################################

def sys_stat(request):
    call_command('versions')
    return HttpResponseRedirect('/admin/')

def backup_stat(request):
    get_backup_stat()
    return HttpResponseRedirect('/admin/backup/')

def backup_form(request):
    return HttpResponse(simplejson.dumps(get_backup_form()), content_type='application/json')

def backup_now(request):
    call_command('backup')
    return backup_stat(request)

def upload_now(request):
    call_command('gdrive')
    return backup_stat(request)


def apache_stat(request):
    return HttpResponse(restyle_apache(), content_type='application/json')

def apache(request):
    return render(request, PATH.HTML_PATH['admin_apache'], {'host_name': env('SSL_HOST')})


def aws(request):
    return render(request, PATH.HTML_PATH['admin_aws'], {'timezone': TIME_ZONE})

def aws_stat(request):
    json = aws_stats(request)
    if isinstance(json, HttpResponse): return json
    return HttpResponse(json, content_type='application/json')

def ga(request):
    return render(request, PATH.HTML_PATH['admin_ga'], {'ga_url': GA['LINK_URL']})

def ga_stat(request):
    json = ga_stats(request)
    if isinstance(json, HttpResponse): return json
    return HttpResponse(json, content_type='application/json')

def git(request):
    return render(request, PATH.HTML_PATH['admin_git'], {'timezone': TIME_ZONE, 'git_repo': GIT['REPOSITORY']})

def git_stat(request):
    json = git_stats(request)
    if isinstance(json, HttpResponse): return json
    return HttpResponse(json, content_type='application/json')


def backup(request):
    flag = -1
    if request.method == 'POST':
        flag = set_backup_form(request)

    form = BackupForm(initial=get_backup_form())
    return render(request, PATH.HTML_PATH['admin_backup'], {'form': form, 'flag': flag, 'email': EMAIL_HOST_USER})

def dir(request):
    return render(request, PATH.HTML_PATH['admin_dir'])

def man(request):
    return render(request, PATH.HTML_PATH['admin_man'])

def ref(request):
    return render(request, PATH.HTML_PATH['admin_ref'])


def get_ver(request):
    stats = simplejson.load(open('%s/cache/stat_ver.json' % MEDIA_ROOT, 'r'))
    return HttpResponse(simplejson.dumps(stats, sort_keys=True, indent=' ' * 4), content_type='application/json')

def get_sys(request):
    stats = simplejson.load(open('%s/cache/stat_sys.json' % MEDIA_ROOT, 'r'))
    return HttpResponse(simplejson.dumps(stats, sort_keys=True, indent=' ' * 4), content_type='application/json')

def get_backup(request):
    stats = simplejson.load(open('%s/cache/stat_backup.json' % MEDIA_ROOT, 'r'))
    return HttpResponse(simplejson.dumps(stats, sort_keys=True, indent=' ' * 4), content_type='application/json')


admin.site.register_view('backup/', view=backup, visible=False)
admin.site.register_view('backup_stat/', view=backup_stat, visible=False)
admin.site.register_view('backup_form/', view=backup_form, visible=False)
admin.site.register_view('backup_now/', view=backup_now, visible=False)
admin.site.register_view('upload_now/', view=upload_now, visible=False)

admin.site.register_view('apache_stat/', view=apache_stat, visible=False)
admin.site.register_view('apache/', view=apache, visible=False)

admin.site.register_view('aws/', view=aws, visible=False)
admin.site.register_view('aws_stat/', view=aws_stat, visible=False)

admin.site.register_view('ga/', view=ga, visible=False)
admin.site.register_view('ga_stat/', view=ga_stat, visible=False)

admin.site.register_view('git/', view=git, visible=False)
admin.site.register_view('git_stat/', view=git_stat, visible=False)

admin.site.register_view('dir/', view=dir, visible=False)
admin.site.register_view('man/', view=man, visible=False)
admin.site.register_view('ref/', view=ref, visible=False)

admin.site.register_view('sys_stat/', view=sys_stat, visible=False)
admin.site.register_view('get_ver/', view=get_ver, visible=False)
admin.site.register_view('get_sys/', view=get_sys, visible=False)
admin.site.register_view('get_backup/', view=get_backup, visible=False)
