from django.conf.urls.defaults import *
from inforecords.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^django_publicdb/', include('django_publicdb.foo.urls')),

    (r'^update_check/', 'django_publicdb.histograms.views.update_check'),
    (r'^update_histograms/', 'django_publicdb.histograms.views.update_histograms'),

    (r'^gateway/', 'django_publicdb.histograms.amfgateway.publicgateway'),

    (r'^certificaat/genereer/(.+)/(.+).zip$', genereer),
    (r'^maakconfig$', maakconfig),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
