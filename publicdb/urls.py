from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView

from .inforecords.views import create_datastore_config, create_nagios_config, keys

urlpatterns = [
    path('', RedirectView.as_view(url='show/stations', permanent=False)),

    re_path(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    re_path(r'^api/', include('publicdb.api.urls')),
    re_path(r'^show/', include('publicdb.status_display.urls')),
    re_path(r'^maps/', include('publicdb.maps.urls')),
    re_path(r'^layout/', include('publicdb.station_layout.urls')),
    re_path(r'^analysis-session/', include('publicdb.analysissessions.urls')),
    re_path(r'^software-updates/', include('publicdb.updates.urls')),
    re_path(r'^raw_data/', include('publicdb.raw_data.urls', namespace='raw_data')),
    re_path(r'^data/', include('publicdb.raw_data.urls')),

    path('config/nagios', create_nagios_config, name='nagios_config'),
    path('config/datastore', create_datastore_config, name='datatore_config'),

    re_path(r'^keys/(?P<host>[a-zA-Z0-9_]+)/$', keys, name='keys'),

    path('admin/', admin.site.urls),
]
