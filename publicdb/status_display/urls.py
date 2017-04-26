from django.conf.urls import include, url

from . import views

maps_patterns = ([
    url(r'^$', views.stations_on_map, name="stations_on_map"),
    url(r'^(?P<country>[a-zA-Z \-]+)/$', views.stations_on_map, name="stations_on_map"),
    url(r'^(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/$', views.stations_on_map, name="stations_on_map"),
    url(r'^(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/(?P<subcluster>[a-zA-Z \-]+)/$', views.stations_on_map, name="stations_on_map"),
], 'map')

network_patterns = ([
    url(r'^network/coincidences/$', views.network_coincidences, name="coincidences"),
    url(r'^network/coincidences/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.network_coincidences, name="coincidences"),
], 'network')

station_patterns = ([
    url(r'^(?P<station_number>\d+)/$', views.station, name="station"),
    url(r'^(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.station_data, name="station"),
    url(r'^(?P<station_number>\d+)/status/$', views.station_status, name="station_status"),
    url(r'^(?P<station_number>\d+)/config/$', views.station_config, name="station_config"),
    url(r'^(?P<station_number>\d+)/latest/$', views.station_latest, name="station_latest"),
], 'station')

source_patterns = ([
    url(r'^coincidencetime/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_coincidencetime_histogram_source, name="coincidencetime"),
    url(r'^coincidencenumber/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_coincidencenumber_histogram_source, name="coincidencenumber"),

    url(r'^eventtime/(?P<station_number>\d+)/$', views.get_eventtime_source, name="eventtime"),
    url(r'^eventtime/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_eventtime_histogram_source, name="eventtime"),
    url(r'^pulseheight/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_pulseheight_histogram_source, name="pulseheight"),
    url(r'^pulseintegral/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_pulseintegral_histogram_source, name="pulseintegral"),
    url(r'^singleshistlow/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_singlesratelow_histogram_source, name="singlesratelow"),
    url(r'^singleshisthigh/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_singlesratehigh_histogram_source, name="singlesratehigh"),
    url(r'^zenith/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_zenith_histogram_source, name="zenith"),
    url(r'^azimuth/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_azimuth_histogram_source, name="azimuth"),
    url(r'^barometer/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_barometer_dataset_source, name="barometer"),
    url(r'^temperature/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_temperature_dataset_source, name="temperature"),
    url(r'^singlesratelow/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_singlesratelow_dataset_source, name="singlesratelow_dataset"),
    url(r'^singlesratehigh/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', views.get_singlesratehigh_dataset_source, name="singlesratehigh_dataset"),

    url(r'^electronics/(?P<station_number>\d+)/$', views.get_electronics_config_source, name="electronics"),
    url(r'^voltage/(?P<station_number>\d+)/$', views.get_voltage_config_source, name="voltage"),
    url(r'^current/(?P<station_number>\d+)/$', views.get_current_config_source, name="current"),
    url(r'^gps/(?P<station_number>\d+)/$', views.get_gps_config_source, name="gps"),
    url(r'^trigger/(?P<station_number>\d+)/$', views.get_trigger_config_source, name="trigger"),
    url(r'^layout/(?P<station_number>\d+)/$', views.get_station_layout_source, name="layout"),
    url(r'^detector_timing_offsets/(?P<station_number>\d+)/$', views.get_detector_timing_offsets_source, name="detector_offsets"),
    url(r'^station_timing_offsets/(?P<ref_station_number>\d+)/(?P<station_number>\d+)/$', views.get_station_timing_offsets_source, name="station_offsets"),
], 'source')

app_name = 'status'
urlpatterns = [
    url(r'^stations/$', views.stations, name="stations"),
    url(r'^stations_by_country/$', views.stations_by_country, name="stations_by_country"),
    url(r'^stations_by_name/$', views.stations_by_name, name="stations_by_name"),
    url(r'^stations_by_number/$', views.stations_by_number, name="stations_by_number"),

    url(r'^stations_on_map/', include(maps_patterns)),
    url(r'^network/', include(network_patterns)),
    url(r'^stations/', include(station_patterns)),
    url(r'^source/', include(source_patterns)),

    url(r'^help/$', views.help, name="help"),
]
