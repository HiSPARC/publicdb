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
    url(r'^network/coincidences/$', views.LatestNetworkSummaryRedirectView.as_view(), name="coincidences"),
    url(r'^network/coincidences/' + DATE_REGEX, views.NetworkSummaryDetailView.as_view(), name="coincidences"),
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
    url(r'^{type}/'.format(type=type) + DATE_REGEX, views.get_specific_network_histogram_source, {'type': type}, name=type)
    for type in ['coincidencetime', 'coincidencenumber']
] + [
    # Histograms
    url(r'^{type}/'.format(type=type) + STATION_DATE_REGEX, views.get_specific_histogram_source, {'type': type}, name=type)
    for type in ['eventtime', 'pulseheight', 'pulseintegral', 'singleslow', 'singleshigh', 'zenith', 'azimuth']
] + [
    # Datasets
    url(r'^{type}/'.format(type=type) + STATION_DATE_REGEX, views.get_specific_dataset_source, {'type': type}, name=type)
    for type in ['barometer', 'temperature', 'singlesratelow', 'singlesratehigh']
] + [
    # Configurations
    url(r'^{type}/(?P<station_number>\d+)/$'.format(type=type), views.get_specific_config_source, {'type': type}, name=type)
    for type in ['electronics', 'voltage', 'current', 'gps', 'trigger']
] + [
    # Histograms
    url(r'^eventtime/(?P<station_number>\d+)/$', views.get_eventtime_source, name='eventtime'),

    # Configurations
    url(r'^layout/(?P<station_number>\d+)/$', views.get_station_layout_source, name='layout'),

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
    url(r'^stations_by_status/$', views.stations_by_status, name="stations_by_status"),

    url(r'^stations_on_map/', include((maps_patterns, 'map'))),
    url(r'^network/', include((network_patterns, 'network'))),
    url(r'^stations/', include((station_patterns, 'station'))),
    url(r'^source/', include((source_patterns, 'source'))),

    url(r'^help/$', views.help, name="help"),
]
