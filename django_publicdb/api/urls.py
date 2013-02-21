from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.api.views',
    (r'^stations/$', 'stations'),
    (r'^subclusters/$', 'subclusters'),
    (r'^clusters/$', 'clusters'),
    (r'^countries/$', 'countries'),

    (r'^subclusters/(?P<subcluster_id>\d+)/$', 'stations'),
    (r'^clusters/(?P<cluster_id>\d+)/$', 'subclusters'),
    (r'^countries/(?P<country_id>\d+)/$', 'clusters'),

    (r'^station/(?P<station_id>\d+)/$', 'station'),

    (r'^station/(?P<station_id>\d+)/data/$', 'has_data'),
    (r'^station/(?P<station_id>\d+)/data/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'has_data'),
    (r'^station/(?P<station_id>\d+)/weather/$', 'has_weather'),
    (r'^station/(?P<station_id>\d+)/weather/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'has_weather'),
    (r'^station/(?P<station_id>\d+)/config/$', 'config'),
    (r'^station/(?P<station_id>\d+)/config/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'config'),

    (r'^station/(?P<station_id>\d+)/num_events/$', 'num_events'),
    (r'^station/(?P<station_id>\d+)/num_events/(?P<year>\d{4})/$', 'num_events_year'),
    (r'^station/(?P<station_id>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d+)/$', 'num_events_month'),
    (r'^station/(?P<station_id>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'num_events_day'),
    (r'^station/(?P<station_id>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/$', 'num_events_hour'),
)
