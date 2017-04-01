from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^stations/$', views.stations),
    url(r'^stations_by_country/$', views.stations_by_country),
    url(r'^stations_by_name/$', views.stations_by_name),
    url(r'^stations_by_number/$', views.stations_by_number),
    url(r'^stations_on_map/$', views.stations_on_map),
    url(r'^stations_on_map/(?P<country>[a-zA-Z \-]+)/$', views.stations_on_map),
    url(r'^stations_on_map/(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/$', views.stations_on_map),
    url(r'^stations_on_map/(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/(?P<subcluster>[a-zA-Z \-]+)/$', views.stations_on_map),

    url(r'^network/coincidences/$', views.network_coincidences),
    url(r'^network/coincidences/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.network_coincidences),

    url(r'^stations/(?P<station_number>\d+)/$', views.station),
    url(r'^stations/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.station_data),
    url(r'^stations/(?P<station_number>\d+)/status/$', views.station_status),
    url(r'^stations/(?P<station_number>\d+)/config/$', views.station_config),
    url(r'^stations/(?P<station_number>\d+)/latest/$', views.station_latest),

    url(r'^source/coincidencetime/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_coincidencetime_histogram_source),
    url(r'^source/coincidencenumber/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_coincidencenumber_histogram_source),

    url(r'^source/eventtime/(?P<station_number>\d+)/$', views.get_eventtime_source),
    url(r'^source/eventtime/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_eventtime_histogram_source),
    url(r'^source/pulseheight/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_pulseheight_histogram_source),
    url(r'^source/pulseintegral/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_pulseintegral_histogram_source),
    url(r'^source/singleshistlow/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_singlesratelow_histogram_source),
    url(r'^source/singleshisthigh/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_singlesratehigh_histogram_source),
    url(r'^source/zenith/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_zenith_histogram_source),
    url(r'^source/azimuth/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_azimuth_histogram_source),
    url(r'^source/barometer/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_barometer_dataset_source),
    url(r'^source/temperature/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_temperature_dataset_source),
    url(r'^source/singlesratelow/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_singlesratelow_dataset_source),
    url(r'^source/singlesratehigh/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_singlesratehigh_dataset_source),

    url(r'^source/electronics/(?P<station_number>\d+)/$', views.get_electronics_config_source),
    url(r'^source/voltage/(?P<station_number>\d+)/$', views.get_voltage_config_source),
    url(r'^source/current/(?P<station_number>\d+)/$', views.get_current_config_source),
    url(r'^source/gps/(?P<station_number>\d+)/$', views.get_gps_config_source),
    url(r'^source/trigger/(?P<station_number>\d+)/$', views.get_trigger_config_source),
    url(r'^source/layout/(?P<station_number>\d+)/$', views.get_station_layout_source),
    url(r'^source/detector_timing_offsets/(?P<station_number>\d+)/$', views.get_detector_timing_offsets_source),
    url(r'^source/station_timing_offsets/(?P<ref_station_number>\d+)/(?P<station_number>\d+)/$', views.get_station_timing_offsets_source),

    url(r'^help/$', views.help),
]
