from django.conf.urls import patterns, include, url, handler404, handler500
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
# admin.autodiscover()

from repository.helper.helper_api import *
from settings import MEDIA_ROOT
from repository import views

urlpatterns = patterns('',
    (r'^$', views.index),
    (r'^browse/$', views.browse),

    (r'^help/about$', views.about),
    (r'^help/license$', views.license),
    (r'^help/history$', views.history),

    (r'^detail/(?P<rmdb_id>\w{,20})$', views.detail),
    (r'^get_area_peaks/$', views.get_area_peaks),

    (r'^deposit/specs/(?P<section>\w{,20})$', views.specs),
    (r'^deposit/validate/$', views.validate),
    (r'^deposit/submit/$', views.upload),
    (r'^deposit/admin_rev_stat/$', views.admin_rev_stat),

    (r'^analyze/predict/$', views.predict),
    (r'^analyze/view/$', views.str_view),

    (r'^tools/$', views.tools),
    (r'^tools/mapseeker/license/$', views.license_mapseeker),
    (r'^tools/mapseeker/download/$', views.download_mapseeker),

    (r'^tools/docs/predict/$', views.tutorial_predict),
    (r'^tools/docs/api/$', views.tutorial_api),
    (r'^tools/docs/rdatkit/$', views.tutorial_rdatkit),
    (r'^tools/docs/hitrace/$', views.tutorial_hitrace),
    (r'^tools/docs/mapseeker/$', views.tutorial_mapseeker),

    (r'^search/$', views.search),
    (r'^advanced_search/$', views.advanced_search),

    (r'^login/$', views.user_login),
    (r'^register/$', views.register),
    (r'^logout/$', views.user_logout),

    (r'^render_structure$', views.render_structure),

    (r'^api/entry/fetch/(?P<rmdb_id>\w+)$', api_fetch_entry),
    (r'^api/entry/all$', api_all_entries),
    (r'^api/entry/organism/(?P<organism_id>\w+)$', api_entries_by_organism),
    (r'^api/entry/system/(?P<system_id>\w+)$', api_entries_by_system),
    (r'^api/rmdbid/organism/(?P<organism_id>\w+)$', api_rmdb_ids_by_organism),
    (r'^api/rmdbid/system/(?P<system_id>\w+)$', api_rmdb_ids_by_system),
    (r'^api/rmdbid/all$', api_all_rmdb_ids),
    (r'^api/organism/all$', api_all_organisms),
    (r'^api/system/all$', api_all_systems),

    (r'^api/index/stats/$', api_stats),
    (r'^api/index/latest/$', api_latest),
    (r'^api/index/news/$', api_news),
    (r'^api/index/history/$', api_history), 
    (r'^api/index/rnastr_ver/$', api_rnastr_ver), 
    (r'^api/index/browse/(?P<keyword>\w+)$', api_browse),
    (r'^api/index/search/(?P<keyword>\w+)/(?P<sstring>.+)$', api_search),

    (r'^test/$', views.test),

    (r'^site_media/isatab_files/(?P<path>.*)$', api_redirect),
    (r'^site_media/rdat_files/(?P<path>.*)$', api_redirect),
    (r'^repository/(?P<path>.*)$', views.url_redirect),

    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT+'/media'}),
    (r'^site_data/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT+'/data'}),
    (r'^site_src/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT+'/misc'}),

    url(r'^admin/', include(admin.site.urls)),
)

handler404 = views.error404
handler500 = views.error500

