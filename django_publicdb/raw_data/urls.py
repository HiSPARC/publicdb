from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.raw_data',
    (r'^$', 'views.download_form'),
    (r'^rpc$', 'views.call_xmlrpc'),
    (r'^(?P<station_id>\d+)/events$', 'views.download_events'),
)
