from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from .inforecords.views import create_datastore_config, keys

urlpatterns = [
    path('', RedirectView.as_view(url='show/stations', permanent=False)),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('api/', include('publicdb.api.urls')),
    path('show/', include('publicdb.status_display.urls')),
    path('maps/', include('publicdb.maps.urls')),
    path('layout/', include('publicdb.station_layout.urls')),
    path('analysis-session/', include('publicdb.analysissessions.urls')),
    path('software-updates/', include('publicdb.updates.urls')),
    path('raw_data/', include('publicdb.raw_data.urls', namespace='raw_data')),
    path('data/', include('publicdb.raw_data.urls')),
    path('config/datastore', create_datastore_config, name='datatore_config'),
    path('keys/<slug:host>/', keys, name='keys'),
    path('admin/', admin.site.urls),
]
