from django.conf.urls import patterns

urlpatterns = patterns('django_publicdb.status_display.views',
    (r'^stations/$', 'stations'),
    (r'^stations_by_country/$', 'stations_by_country'),
    (r'^stations_by_name/$', 'stations_by_name'),
    (r'^stations_by_number/$', 'stations_by_number'),
    (r'^stations_on_map/$', 'stations_on_map'),
    (r'^stations_on_map/(?P<country>[a-zA-Z \-]+)/$', 'stations_on_map'),
    (r'^stations_on_map/(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/$', 'stations_on_map'),
    (r'^stations_on_map/(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/(?P<subcluster>[a-zA-Z \-]+)/$', 'stations_on_map'),

    (r'^network/coincidences/$', 'network_coincidences'),
    (r'^network/coincidences/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'network_coincidences'),

    (r'^stations/(?P<station_number>\d+)/$', 'station'),
    (r'^stations/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'station_data'),
    (r'^stations/(?P<station_number>\d+)/status/$', 'station_status'),
    (r'^stations/(?P<station_number>\d+)/config/$', 'station_config'),
    (r'^stations/(?P<station_number>\d+)/latest/$', 'station_latest'),

    (r'^source/coincidencetime/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_coincidencetime_histogram_source'),
    (r'^source/coincidencenumber/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_coincidencenumber_histogram_source'),

    (r'^source/eventtime/(?P<station_number>\d+)/$', 'get_eventtime_source'),
    (r'^source/eventtime/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_eventtime_histogram_source'),
    (r'^source/pulseheight/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_pulseheight_histogram_source'),
    (r'^source/pulseintegral/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_pulseintegral_histogram_source'),
    (r'^source/barometer/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_barometer_dataset_source'),
    (r'^source/temperature/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'get_temperature_dataset_source'),
    (r'^source/voltage/(?P<station_number>\d+)/$', 'get_voltage_config_source'),
    (r'^source/current/(?P<station_number>\d+)/$', 'get_current_config_source'),
    (r'^source/gps/(?P<station_number>\d+)/$', 'get_gps_config_source'),
    (r'^source/trigger/(?P<station_number>\d+)/$', 'get_trigger_config_source'),
    (r'^source/layout/(?P<station_number>\d+)/$', 'get_station_layout_source'),
    (r'^source/detector_timing_offsets/(?P<station_number>\d+)/$', 'get_detector_timing_offsets_source'),

    (r'^help/$', 'help'),
)
