from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView

from .inforecords.views import create_nagios_config, create_datastore_config, keys

urlpatterns = [
    (r'^$', RedirectView.as_view(url='show/stations', permanent=False)),

    (r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    (r'^api/', include('publicdb.api.urls')),
    (r'^show/', include('publicdb.status_display.urls')),
    (r'^maps/', include('publicdb.maps.urls')),
    (r'^layout/', include('publicdb.station_layout.urls')),
    (r'^analysis-session/', include('publicdb.analysissessions.urls')),
    (r'^jsparc/', include('publicdb.jsparc.urls')),
    (r'^software-updates/', include('publicdb.updates.urls')),
    (r'^raw_data/', include('publicdb.raw_data.urls')),
    (r'^data/', include('publicdb.raw_data.urls')),

    (r'^config/nagios$', create_nagios_config),
    (r'^config/datastore$', create_datastore_config),

    (r'^keys/(?P<host>\w+)/$', keys),

    (r'^admin/', include(admin.site.urls)),
]
