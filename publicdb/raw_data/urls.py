from django.conf.urls import url
from django.views.generic import RedirectView

from . import views

app_name = 'data'
urlpatterns = [
    url(r'^$', RedirectView.as_view(url='download', permanent=False)),
    url(r'^download/$', views.download_form, name="download_form"),
    url(r'^download/(?P<station_number>\d+)/(?P<start>[^/]+)/(?P<end>[^/]+)/$', views.download_form, name="download_form"),
    url(r'^download/coincidences/$', views.coincidences_download_form, name="download_coincidences_form"),
    url(r'^download/coincidences/(?P<start>[^/]+)/(?P<end>[^/]+)/$', views.coincidences_download_form, name="download_coincidences_form"),
    url(r'^rpc$', views.call_xmlrpc, name="rpc"),
    url(r'^(?P<station_number>\d+)/events/$', views.download_data, {'data_type': 'events'}, name="events"),
    url(r'^(?P<station_number>\d+)/weather/$', views.download_data, {'data_type': 'weather'}, name="weather"),
    url(r'^(?P<station_number>\d+)/singles/$', views.download_data, {'data_type': 'singles'}, name="singles"),
    url(r'^knmi/lightning/(?P<lightning_type>\d+)/$', views.download_data, {'data_type': 'lightning'}, name="lightning"),
    url(r'^network/coincidences/$', views.download_coincidences, name="coincidences"),
]
