from django.conf.urls import patterns
from django.views.generic import RedirectView

urlpatterns = patterns('django_publicdb.raw_data',
    (r'^$', RedirectView.as_view(url='download')),
    (r'^download/$', 'views.download_form'),
    (r'^download/(?P<station_number>\d+)/(?P<start>[^/]+)/(?P<end>[^/]+)/$', 'views.download_form'),
    (r'^download/coincidences/$', 'views.coincidences_download_form'),
    (r'^download/coincidences/(?P<start>[^/]+)/(?P<end>[^/]+)/$', 'views.coincidences_download_form'),
    (r'^rpc$', 'views.call_xmlrpc'),
    (r'^(?P<station_number>\d+)/events/$', 'views.download_data', {'data_type': 'events'}),
    (r'^(?P<station_number>\d+)/weather/$', 'views.download_data', {'data_type': 'weather'}),
    (r'^(?P<station_number>\d+)/singles/$', 'views.download_data', {'data_type': 'singles'}),
    (r'^knmi/lightning/(?P<lightning_type>\d+)/$', 'views.download_data', {'data_type': 'lightning'}),
    (r'^network/coincidences/$', 'views.download_coincidences'),
)
