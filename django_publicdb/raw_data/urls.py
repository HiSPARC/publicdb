from django.conf.urls import patterns
from django.views.generic import RedirectView

urlpatterns = patterns('django_publicdb.raw_data',
    (r'^$', RedirectView.as_view(url='download')),
    (r'^download$', 'views.download_form'),
    (r'^download/(?P<station_id>\d+)/(?P<start>[^/]+)/(?P<end>[^/]+)$', 'views.download_form'),
    (r'^rpc$', 'views.call_xmlrpc'),
    (r'^(?P<station_id>\d+)/events$', 'views.download_data', {'data_type': 'events'}),
    (r'^(?P<station_id>\d+)/weather$', 'views.download_data', {'data_type': 'weather'}),
)
