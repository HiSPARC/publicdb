from django.conf.urls import patterns

urlpatterns = patterns('django_publicdb.api.views',
    (r'^$', 'man'),

    (r'^stations/$', 'stations'),
    (r'^subclusters/$', 'subclusters'),
    (r'^clusters/$', 'clusters'),
    (r'^countries/$', 'countries'),

    (r'^subclusters/(?P<subcluster_number>\d+)/$', 'stations'),
    (r'^clusters/(?P<cluster_number>\d+)/$', 'subclusters'),
    (r'^countries/(?P<country_number>\d+)/$', 'clusters'),

    (r'^stations/data/$', 'stations_with_data', {'type': 'events'}),
    (r'^stations/data/(?P<year>\d{4})/$', 'stations_with_data', {'type': 'events'}),
    (r'^stations/data/(?P<year>\d{4})/(?P<month>\d+)/$', 'stations_with_data', {'type': 'events'}),
    (r'^stations/data/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'stations_with_data', {'type': 'events'}),
    (r'^stations/weather/$', 'stations_with_data', {'type': 'weather'}),
    (r'^stations/weather/(?P<year>\d{4})/$', 'stations_with_data', {'type': 'weather'}),
    (r'^stations/weather/(?P<year>\d{4})/(?P<month>\d+)/$', 'stations_with_data', {'type': 'weather'}),
    (r'^stations/weather/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'stations_with_data', {'type': 'weather'}),

    (r'^station/(?P<station_number>\d+)/$', 'station'),
    (r'^station/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'station'),

    (r'^station/(?P<station_number>\d+)/data/$', 'has_data'),
    (r'^station/(?P<station_number>\d+)/data/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'has_data'),
    (r'^station/(?P<station_number>\d+)/weather/$', 'has_weather'),
    (r'^station/(?P<station_number>\d+)/weather/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'has_weather'),
    (r'^station/(?P<station_number>\d+)/config/$', 'config'),
    (r'^station/(?P<station_number>\d+)/config/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'config'),

    (r'^station/(?P<station_number>\d+)/num_events/$', 'num_events'),
    (r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/$', 'num_events'),
    (r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d+)/$', 'num_events'),
    (r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'num_events'),
    (r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/$', 'num_events'),

    (r'^station/(?P<station_number>\d+)/trace/(?P<ext_timestamp>\d+)/$', 'get_event_traces'),

    (r'^station/(?P<station_number>\d+)/plate/(?P<plate_number>\d+)/pulseheight/fit/$', 'get_pulseheight_fit'),
    (r'^station/(?P<station_number>\d+)/plate/(?P<plate_number>\d+)/pulseheight/fit/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_pulseheight_fit'),
    (r'^station/(?P<station_number>\d+)/plate/(?P<plate_number>\d+)/pulseheight/drift/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<number_of_days>\d+)/$', 'get_pulseheight_drift'),
    (r'^station/(?P<station_number>\d+)/plate/(?P<plate_number>\d+)/pulseheight/drift/last_14_days/$', 'get_pulseheight_drift_last_14_days'),
    (r'^station/(?P<station_number>\d+)/plate/(?P<plate_number>\d+)/pulseheight/drift/last_30_days/$', 'get_pulseheight_drift_last_30_days'),
)
