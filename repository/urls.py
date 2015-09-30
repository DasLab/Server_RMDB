from django.conf.urls import include, url, handler404, handler500
from django.contrib import admin
# from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from adminplus.sites import AdminSitePlus
from filemanager import path_end

from repository.settings import MEDIA_ROOT, STATIC_ROOT, STATIC_URL, DEBUG
from repository import views
from repository.helper.helper_api import *

admin.site = AdminSitePlus()
admin.site.index_title = 'RMDB'
admin.autodiscover()
# admin.site.login = views.admin_login
admin.site.logout = views.user_logout


urlpatterns = [
    url(r'^$', views.index),
    url(r'^browse/$', views.browse),

    url(r'^help/about$', views.about),
    url(r'^help/license$', views.license),
    url(r'^help/history$', views.history),

    url(r'^detail/(?P<rmdb_id>\w{,20})$', views.detail),
    url(r'^get_area_peaks/$', views.get_area_peaks),

    url(r'^deposit/specs/(?P<section>\w{,20})$', views.specs),
    url(r'^deposit/validate/$', views.validate),
    url(r'^deposit/submit/$', views.upload),
    url(r'^deposit/admin_rev_stat/$', views.admin_rev_stat),

    url(r'^analyze/predict/$', views.predict),
    url(r'^analyze/view/$', views.str_view),

    url(r'^tools/$', views.tools),
    url(r'^tools/(?P<keyword>\w+)/license/$', views.tools_license),
    url(r'^tools/(?P<keyword>\w+)/download/$', views.tools_download),

    url(r'^tools/docs/(?P<keyword>\w+)/$', views.tutorial),
    url(r'^rdatkit/$', views.tutorial, {'keyword':'rdatkit'}),
    url(r'^hitrace/$', views.tutorial, {'keyword':'hitrace'}),
    url(r'^mapseeker/$', views.tutorial, {'keyword':'mapseeker'}),
    url(r'^reeffit/$', views.tutorial, {'keyword':'reeffit'}),

    url(r'^search/$', views.search),
    url(r'^advanced_search/$', views.advanced_search),

    url(r'^login/$', views.user_login),
    url(r'^register/$', views.register),
    url(r'^logout/$', views.user_logout),

    url(r'^render_structure$', views.render_structure),

    url(r'^api/entry/fetch/(?P<rmdb_id>\w+)$', api_fetch_entry),
    url(r'^api/entry/all$', api_all_entries),
    url(r'^api/entry/organism/(?P<organism_id>\w+)$', api_entries_by_organism),
    url(r'^api/entry/system/(?P<system_id>\w+)$', api_entries_by_system),
    url(r'^api/rmdbid/organism/(?P<organism_id>\w+)$', api_rmdb_ids_by_organism),
    url(r'^api/rmdbid/system/(?P<system_id>\w+)$', api_rmdb_ids_by_system),
    url(r'^api/rmdbid/all$', api_all_rmdb_ids),
    url(r'^api/organism/all$', api_all_organisms),
    url(r'^api/system/all$', api_all_systems),

    url(r'^api/index/stats/$', api_stats),
    url(r'^api/index/latest/$', api_latest),
    url(r'^api/index/news/$', api_news),
    url(r'^api/index/history/$', api_history), 
    url(r'^api/index/rnastr_ver/$', api_rnastr_ver), 
    url(r'^api/index/browse/(?P<keyword>\w+)$', api_browse),
    url(r'^api/index/search/(?P<keyword>\w+)/(?P<sstring>.+)$', api_search),

    url(r'^get_admin/$', views.get_admin),
    url(r'^get_js/$', views.get_js),
    url(r'^api/test/$', api_test),
    url(r'^repository/(?P<path>.*)$', views.url_redirect),

    url(r'^site_media/isatab_files/(?P<path>.*)$', api_redirect),
    url(r'^site_media/rdat_files/(?P<path>.*)$', api_redirect),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT+'/media'}),
    url(r'^site_data/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT+'/data'}),
    url(r'^site_src/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT+'/misc'}),

    url(r'^admin/browse/' + path_end, views.browse),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?:robots.txt)?$', 'django.views.static.serve', kwargs={'path': 'robots.txt', 'document_root': MEDIA_ROOT}),
]

if DEBUG: urlpatterns.append(url(r'^test/$', views.test))
handler404 = views.error404
handler500 = views.error500

