from django.conf.urls import url

from . import views

app_name = 'api'
urlpatterns = [
    url(r'^$', views.man),

    url(r'^stations/$', views.stations),
    url(r'^subclusters/$', views.subclusters),
    url(r'^clusters/$', views.clusters),
    url(r'^countries/$', views.countries),

    url(r'^subclusters/(?P<subcluster_number>\d+)/$', views.stations),
    url(r'^clusters/(?P<cluster_number>\d+)/$', views.subclusters),
    url(r'^countries/(?P<country_number>\d+)/$', views.clusters),

    url(r'^stations/data/$', views.stations_with_data, {'type': 'events'}),
    url(r'^stations/data/(?P<year>\d{4})/$', views.stations_with_data, {'type': 'events'}),
    url(r'^stations/data/(?P<year>\d{4})/(?P<month>\d+)/$', views.stations_with_data, {'type': 'events'}),
    url(r'^stations/data/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.stations_with_data, {'type': 'events'}),
    url(r'^stations/weather/$', views.stations_with_data, {'type': 'weather'}),
    url(r'^stations/weather/(?P<year>\d{4})/$', views.stations_with_data, {'type': 'weather'}),
    url(r'^stations/weather/(?P<year>\d{4})/(?P<month>\d+)/$', views.stations_with_data, {'type': 'weather'}),
    url(r'^stations/weather/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.stations_with_data, {'type': 'weather'}),

    url(r'^station/(?P<station_number>\d+)/$', views.station),
    url(r'^station/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.station),

    url(r'^station/(?P<station_number>\d+)/data/$', views.has_data, {'type': 'events'}),
    url(r'^station/(?P<station_number>\d+)/data/(?P<year>\d{4})/$', views.has_data, {'type': 'events'}),
    url(r'^station/(?P<station_number>\d+)/data/(?P<year>\d{4})/(?P<month>\d+)/$', views.has_data, {'type': 'events'}),
    url(r'^station/(?P<station_number>\d+)/data/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.has_data, {'type': 'events'}),
    url(r'^station/(?P<station_number>\d+)/weather/$', views.has_data, {'type': 'weather'}),
    url(r'^station/(?P<station_number>\d+)/weather/(?P<year>\d{4})/$', views.has_data, {'type': 'weather'}),
    url(r'^station/(?P<station_number>\d+)/weather/(?P<year>\d{4})/(?P<month>\d+)/$', views.has_data, {'type': 'weather'}),
    url(r'^station/(?P<station_number>\d+)/weather/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.has_data, {'type': 'weather'}),
    url(r'^station/(?P<station_number>\d+)/config/$', views.config),
    url(r'^station/(?P<station_number>\d+)/config/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.config),

    url(r'^station/(?P<station_number>\d+)/num_events/$', views.num_events),
    url(r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/$', views.num_events),
    url(r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d+)/$', views.num_events),
    url(r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.num_events),
    url(r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/$', views.num_events),

    url(r'^station/(?P<station_number>\d+)/trace/(?P<ext_timestamp>\d+)/$', views.get_event_traces),

    url(r'^station/(?P<station_number>\d+)/plate/(?P<plate_number>\d+)/pulseheight/fit/$', views.get_pulseheight_fit),
    url(r'^station/(?P<station_number>\d+)/plate/(?P<plate_number>\d+)/pulseheight/fit/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_pulseheight_fit),
    url(r'^station/(?P<station_number>\d+)/plate/(?P<plate_number>\d+)/pulseheight/drift/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<number_of_days>\d+)/$', views.get_pulseheight_drift),
    url(r'^station/(?P<station_number>\d+)/plate/(?P<plate_number>\d+)/pulseheight/drift/last_14_days/$', views.get_pulseheight_drift_last_14_days),
    url(r'^station/(?P<station_number>\d+)/plate/(?P<plate_number>\d+)/pulseheight/drift/last_30_days/$', views.get_pulseheight_drift_last_30_days),
]
