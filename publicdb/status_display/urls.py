from django.conf.urls import include, url

from . import views

DATE_REGEX = r'(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$'
STATION_DATE_REGEX = r'(?P<station_number>\d+)/' + DATE_REGEX


maps_patterns = [
    url(r'^$', views.stations_on_map, name="stations_on_map"),
    url(r'^(?P<country>[a-zA-Z \-]+)/$', views.stations_on_map, name="stations_on_map"),
    url(r'^(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/$', views.stations_on_map, name="stations_on_map"),
    url(r'^(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/(?P<subcluster>[a-zA-Z \-]+)/$', views.stations_on_map, name="stations_on_map"),
]

network_patterns = [
    url(r'^network/coincidences/$', views.network_coincidences, name="coincidences"),
    url(r'^network/coincidences/' + DATE_REGEX, views.network_coincidences, name="coincidences"),
]

station_patterns = [
    url(r'^(?P<station_number>\d+)/$', views.LatestSummaryRedirectView.as_view(), name="data"),
    url(r'^' + STATION_DATE_REGEX, views.SummaryDetailView.as_view(), name="data"),
    url(r'^(?P<station_number>\d+)/status/$', views.station_status, name="status"),
    url(r'^(?P<station_number>\d+)/config/$', views.station_config, name="config"),
    url(r'^(?P<station_number>\d+)/latest/$', views.station_latest, name="latest"),
]

source_patterns = [
    # Network histograms
    url(r'^coincidencetime/' + DATE_REGEX, views.get_coincidencetime_histogram_source, name="coincidencetime"),
    url(r'^coincidencenumber/' + DATE_REGEX, views.get_coincidencenumber_histogram_source, name="coincidencenumber"),

    # Histograms
    url(r'^eventtime/(?P<station_number>\d+)/$', views.get_eventtime_source, name="eventtime"),
    url(r'^eventtime/' + STATION_DATE_REGEX, views.get_eventtime_histogram_source, name="eventtime"),
    url(r'^pulseheight/' + STATION_DATE_REGEX, views.get_pulseheight_histogram_source, name="pulseheight"),
    url(r'^pulseintegral/' + STATION_DATE_REGEX, views.get_pulseintegral_histogram_source, name="pulseintegral"),
    url(r'^singleshistlow/' + STATION_DATE_REGEX, views.get_singlesratelow_histogram_source, name="singleslow"),
    url(r'^singleshisthigh/' + STATION_DATE_REGEX, views.get_singlesratehigh_histogram_source, name="singleshigh"),
    url(r'^zenith/' + STATION_DATE_REGEX, views.get_zenith_histogram_source, name="zenith"),
    url(r'^azimuth/' + STATION_DATE_REGEX, views.get_azimuth_histogram_source, name="azimuth"),

    # Datasets
    url(r'^barometer/' + STATION_DATE_REGEX, views.get_barometer_dataset_source, name="barometer"),
    url(r'^temperature/' + STATION_DATE_REGEX, views.get_temperature_dataset_source, name="temperature"),
    url(r'^singlesratelow/' + STATION_DATE_REGEX, views.get_singlesratelow_dataset_source, name="singlesratelow"),
    url(r'^singlesratehigh/' + STATION_DATE_REGEX, views.get_singlesratehigh_dataset_source, name="singlesratehigh"),

    # Configurations
    url(r'^electronics/(?P<station_number>\d+)/$', views.get_electronics_config_source, name="electronics"),
    url(r'^voltage/(?P<station_number>\d+)/$', views.get_voltage_config_source, name="voltage"),
    url(r'^current/(?P<station_number>\d+)/$', views.get_current_config_source, name="current"),
    url(r'^gps/(?P<station_number>\d+)/$', views.get_gps_config_source, name="gps"),
    url(r'^trigger/(?P<station_number>\d+)/$', views.get_trigger_config_source, name="trigger"),
    url(r'^layout/(?P<station_number>\d+)/$', views.get_station_layout_source, name="layout"),

    # Calibrations
    url(r'^detector_timing_offsets/(?P<station_number>\d+)/$', views.get_detector_timing_offsets_source, name="detector_offsets"),
    url(r'^station_timing_offsets/(?P<ref_station_number>\d+)/(?P<station_number>\d+)/$', views.get_station_timing_offsets_source, name="station_offsets"),
]

app_name = 'status'
urlpatterns = [
    url(r'^stations/$', views.stations, name="stations"),
    url(r'^stations_by_country/$', views.stations_by_country, name="stations_by_country"),
    url(r'^stations_by_name/$', views.stations_by_name, name="stations_by_name"),
    url(r'^stations_by_number/$', views.stations_by_number, name="stations_by_number"),

    url(r'^stations_on_map/', include((maps_patterns, 'map'))),
    url(r'^network/', include((network_patterns, 'network'))),
    url(r'^stations/', include((station_patterns, 'station'))),
    url(r'^source/', include((source_patterns, 'source'))),

    url(r'^help/$', views.help, name="help"),
]
