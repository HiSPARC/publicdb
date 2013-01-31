from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.api.views',
    (r'^station/$', 'station'),
    (r'^subcluster/$', 'subcluster'),
    (r'^cluster/$', 'cluster'),
    (r'^country/$', 'country'),

    (r'^station/(?P<subcluster_name>[a-zA-Z \-]+)/$', 'station'),
    (r'^subcluster/(?P<cluster_name>[a-zA-Z \-]+)/$', 'subcluster'),
    (r'^cluster/(?P<country_name>[a-zA-Z \-]+)/$', 'cluster'),

    (r'^station/(?P<station_id>\d+)/$', 'station_info'),

    (r'^station/(?P<station_id>\d+)/data/$', 'has_data'),
    (r'^station/(?P<station_id>\d+)/weather/$', 'has_weather'),
    (r'^station/(?P<station_id>\d+)/config/$', 'config'),

    (r'^station/(?P<station_id>\d+)/data/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'has_data'),
    (r'^station/(?P<station_id>\d+)/weather/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'has_weather'),
    (r'^station/(?P<station_id>\d+)/config/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'config'),
)
