from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('repository.views',
    (r'^$', 'index'),
    (r'^browse/$', 'browse'),

    (r'^help/about$', 'about'),
    (r'^help/license$', 'license'),
    (r'^help/history$', 'history'),

    (r'^detail/(?P<rmdb_id>\w{,20})$', 'detail'),
    (r'^get_area_peaks/$', 'get_area_peaks'),

    (r'^deposit/specs/(?P<section>\w{,20})$', 'specs'),
    (r'^deposit/validate/$', 'validate'),
    (r'^deposit/submit/$', 'upload'),

    (r'^analyze/predict/$', 'predict'),
    (r'^analyze/tools/$', 'tools'),
    (r'^analyze/tools/mapseeker/license/$', 'license_mapseeker'),
    (r'^analyze/tools/mapseeker/download/$', 'download_mapseeker'),

    (r'^analyze/docs/predict/$', 'tutorial_predict'),
    (r'^analyze/docs/api/$', 'tutorial_api'),
    (r'^analyze/docs/rdatkit/$', 'tutorial_rdatkit'),
    (r'^analyze/docs/hitrace/$', 'tutorial_hitrace'),
    (r'^analyze/docs/mapseeker/$', 'tutorial_mapseeker'),

    (r'^search/$', 'search'),
    (r'^advanced_search/$', 'advanced_search'),

    (r'^login/$', 'user_login'),
    (r'^register/$', 'register'),
    (r'^logout/$', 'user_logout'),

    (r'^render_structure$', 'render_structure'),

    (r'^api/entry/fetch/(?P<rmdb_id>\w+)$', 'api_fetch_entry'),
    (r'^api/entry/all$', 'api_all_entries'),
    (r'^api/entry/organism/(?P<organism_id>\w+)$', 'api_entries_by_organism'),
    (r'^api/entry/system/(?P<system_id>\w+)$', 'api_entries_by_system'),
    (r'^api/rmdbid/organism/(?P<organism_id>\w+)$', 'api_rmdb_ids_by_organism'),
    (r'^api/rmdbid/system/(?P<system_id>\w+)$', 'api_rmdb_ids_by_system'),
    (r'^api/rmdbid/all$', 'api_all_rmdb_ids'),
    (r'^api/organism/all$', 'api_all_organisms'),
    (r'^api/system/all$', 'api_all_systems'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
