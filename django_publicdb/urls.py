from django.conf.urls.defaults import *
from django.views.generic import RedirectView

from django_publicdb.inforecords.views import *

#Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^django_publicdb/', include('django_publicdb.foo.urls')),

    (r'^$', RedirectView.as_view(url='show/stations', permanent=False)),

    (r'^api/', include('django_publicdb.api.urls')),
    (r'^show/', include('django_publicdb.status_display.urls')),
    (r'^live/', include('django_publicdb.live.urls')),
    (r'^analysis-session/', include('django_publicdb.analysissessions.urls')),
    (r'^software-updates/', include('django_publicdb.updates.urls')),
    (r'^raw_data/', include('django_publicdb.raw_data.urls')),

    (r'^config/nagios$', create_nagios_config),
    (r'^config/datastore$', create_datastore_config),

    (r'^keys/(?P<host>\w+)/$', 'django_publicdb.inforecords.views.keys'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^jsparc/', include('django_publicdb.jsparc.urls')),
)
