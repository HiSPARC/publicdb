from django.conf.urls.defaults import *
from django.contrib import admin
from inforecords.views import *

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^certificaat/genereer/(.+)/(.+).zip$', genereer),
    (r'^maakconfig$', maakconfig),
    (r'^$', indexpagina),
)
