from django.conf.urls.defaults import *

from settings import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'rmdb.views.home'),
    (r'^repository/', include('repository.urls')),
    # (r'^structureserver/', include('structureserver.urls')),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',\
      {'document_root': MEDIA_ROOT}),
    # Example:
    # (r'^rmdb/', include('rmdb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
)
