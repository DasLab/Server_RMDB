from django.conf.urls import include, url, handler400, handler403, handler404, handler500
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.static import serve

from adminplus.sites import AdminSitePlus
from filemanager import path_end

from src.settings import MEDIA_ROOT, DEBUG, IS_MAINTENANCE, env
from src import user
from src import views
from src.util import api
from django.contrib.auth import views as auth_views
from src.models import CustomSetPasswordForm, CustomPasswordResetForm
from env import PATH

# from src.helper.helper_api import *

admin.site = AdminSitePlus()
admin.site.index_title = '%s Administration' % env('SERVER_NAME')
admin.autodiscover()
admin.site.login = user.user_login
admin.site.logout = user.user_logout


if IS_MAINTENANCE:
    urlpatterns = [
        url(r'^ping_test/?$', views.ping_test),
        url(r'^get_admin/?$', views.get_admin),
        url(r'^get_js/?$', views.get_js),

        url(r'^site_media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT + '/media'}),
        url(r'^robots.txt$', serve, kwargs={'path': 'robots.txt', 'document_root': MEDIA_ROOT}),

        url(r'^$', views.error503),
        url(r'^.*/?$', RedirectView.as_view(url='/', permanent=True)),
    ]
else:
    urlpatterns = [
        url(r'^$', views.index),
        url(r'^browse/?$', views.browse),
        url(r'^detail/(?P<rmdb_id>\w{,20})$', views.detail),

        url(r'^help/about/?$', views.about),
        url(r'^help/license/?$', views.license),
        url(r'^help/history/?$', views.history),

        url(r'^deposit/specs/?$', views.specs),
        url(r'^deposit/validate/?$', views.validate),
        url(r'^deposit/submit/?$', views.upload),
        url(r'^deposit/review/?$', views.review),

        # url(r'^analyze/predict/?$', views.predict),
        # url(r'^analyze/view/?$', views.str_view),

        url(r'^tools/?$', views.tools),
        url(r'^tools/license/?(?P<keyword>\w+)/$', views.tools_license),
        url(r'^tools/download/(?P<keyword>\w+)/?$', views.tools_download),
        url(r'^tools/download/(?P<keyword>\w+)/(?P<tag>\w+)/?$', views.tools_link),
        url(r'^tools/docs/(?P<keyword>\w+)/?$', views.tutorial),
        url(r'^rdatkit/?$', views.tutorial, {'keyword': 'rdatkit'}),
        url(r'^hitrace/?$', views.tutorial, {'keyword': 'hitrace'}),
        url(r'^mapseeker/?$', views.tutorial, {'keyword': 'mapseeker'}),
        url(r'^reeffit/?$', views.tutorial, {'keyword': 'reeffit'}),
        url(r'^biers/?$', views.tutorial, {'keyword': 'biers'}),

        url(r'^search/?$', views.search),
        # url(r'^advanced_search/?$', views.advanced_search),

        url(r'^login/?$', user.user_login),
        url(r'^register/?$', user.register),
        url(r'^logout/?$', user.user_logout),
        url(r'^edit_profile/?$', user.edit_profile),
        # url(r'^change_password/?$', auth_views.PasswordChangeView.as_view(template_name=PATH.HTML_PATH['change_password'])),

        # url(r'^change_password/done/?$', auth_views.password_change_done, {'template_name': PATH.HTML_PATH['change_password_done']}, name='password_change_done'),

        # url(r'^change_password/?$', auth_views.PasswordChangeView.as_view()),
        # url("^password_change/done/$", auth_views.PasswordChangeDoneView.as_view()),

        url(r'^change_password/?$', user.change_password),
        url(r'^change_password/done/?$', user.change_password_done, name='change_password_done'),

        url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.password_reset_confirm, {'set_password_form': CustomSetPasswordForm},
            name='password_reset_confirm'),
        url(r'^password_reset/$', auth_views.password_reset,
            {'password_reset_form': CustomPasswordResetForm},name='password_reset'),
        url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
        url(r'^reset/done/?$', auth_views.password_reset_complete, name='password_reset_complete'),

        # url(r'^render_structure/?$', views.render_structure),

        # url(r'^api/entry/fetch/(?P<rmdb_id>\w+)$', api_fetch_entry),
        # url(r'^api/entry/all$', api_all_entries),
        # url(r'^api/entry/organism/(?P<organism_id>\w+)$', api_entries_by_organism),
        # url(r'^api/entry/system/(?P<system_id>\w+)$', api_entries_by_system),
        # url(r'^api/rmdbid/organism/(?P<organism_id>\w+)$', api_rmdb_ids_by_organism),
        # url(r'^api/rmdbid/system/(?P<system_id>\w+)$', api_rmdb_ids_by_system),
        # url(r'^api/rmdbid/all$', api_all_rmdb_ids),
        # url(r'^api/organism/all$', api_all_organisms),
        # url(r'^api/system/all$', api_all_systems),

        # url(r'^api/index/rnastr_ver/$', api_rnastr_ver),
        url(r'^api/search/(?P<sstring>.+)$', api.search),
        url(r'^api/git_hook/?$', api.git_hook),

        url(r'^ping_test/?$', views.ping_test),
        url(r'^get_admin/?$', views.get_admin),
        url(r'^get_user/?$', views.get_user),
        url(r'^get_js/?$', views.get_js),
        url(r'^get_stats/?$', views.get_stats),
        url(r'^get_news/?$', views.get_news),
        url(r'^get_recent/?$', views.get_recent),
        url(r'^get_browse/(?P<keyword>\w+)/?$', views.get_browse),

        url(r'^error/400/?$', views.error400),
        url(r'^error/401/?$', views.error401),
        url(r'^error/403/?$', views.error403),
        url(r'^error/404/?$', views.error404),
        url(r'^error/500/?$', views.error500),
        url(r'^error/503/?$', views.error503),

        url(r'^repository/(?P<path>.*)$', RedirectView.as_view(url='/%(path)s', permanent=True)),
        url(r'^site_media/isatab_files/(?P<path>.*)$', RedirectView.as_view(url='/site_data/file/%(path)s', permanent=True)),
        url(r'^site_media/rdat_files/(?P<path>.*)$', RedirectView.as_view(url='/site_data/file/%(path)s', permanent=True)),
        url(r'^site_media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT + '/media'}),
        url(r'^site_data/tmp/(?P<path>.*)$', RedirectView.as_view(url='/error/403/', permanent=True)),
        url(r'^site_data/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT + '/data'}),

        url(r'^admin/browse/' + path_end, user.browse),
        url(r'^admin/', include(admin.site.urls)),
        url(r'^robots.txt$', serve, kwargs={'path': 'robots.txt', 'document_root': MEDIA_ROOT}),

        url(r'^entry_manage$', views.entry_manage),
        url(r'^entry_manage/entry_edit/(?P<rmdb_id>\w+)/(?P<entry_id>\d+)/?$', views.edit_entry),

        url('^', include('django.contrib.auth.urls')),

    ]

    if DEBUG: urlpatterns.append(url(r'^test/?$', views.test))

handler400 = views.error400
handler403 = views.error403
handler404 = views.error404
handler500 = views.error500
