from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.raw_data',
    (r'^rpc$', 'views.call_xmlrpc'),
    (r'^download/$', 'views.download_form'),
    (r'^download/(?P<station_id>\d+)/(?P<start_date>\d{4}-\d+-\d+)/(?P<end_date>\d{4}-\d+-\d+)/$',
    'views.download_data'),
)
