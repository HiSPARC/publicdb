from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.status_display.views',
    (r'^stations/$', 'stations'),
    (r'^stations/(?P<station_id>\d+)/$', 'station'),
    (r'^stations/(?P<station_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'station_page'),
    (r'^source/eventtime/(?P<station_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_eventtime_histogram_source'),
    (r'^source/pulseheight/(?P<station_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_pulseheight_histogram_source'),
    (r'^source/pulseintegral/(?P<station_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_pulseintegral_histogram_source'),
    (r'^source/barometer/(?P<station_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_barometer_dataset_source'),
    (r'^source/temperature/(?P<station_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_temperature_dataset_source'),
)
