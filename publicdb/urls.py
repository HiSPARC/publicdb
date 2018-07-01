from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

from .inforecords.views import (create_datastore_config, create_nagios_config,
                                keys)

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='show/stations', permanent=False)),

    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    url(r'^api/', include('publicdb.api.urls')),
    url(r'^show/', include('publicdb.status_display.urls')),
    url(r'^maps/', include('publicdb.maps.urls')),
    url(r'^layout/', include('publicdb.station_layout.urls')),
    url(r'^analysis-session/', include('publicdb.analysissessions.urls')),
    url(r'^software-updates/', include('publicdb.updates.urls')),
    url(r'^raw_data/', include('publicdb.raw_data.urls')),
    url(r'^data/', include('publicdb.raw_data.urls')),

    url(r'^config/nagios$', create_nagios_config, name='nagios_config'),
    url(r'^config/datastore$', create_datastore_config, name='datatore_config'),

    url(r'^keys/(?P<host>[a-zA-Z0-9_]+)/$', keys, name='keys'),

    url(r'^admin/', include(admin.site.urls)),
]
