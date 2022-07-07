from django.urls import include, path, re_path

from . import views

DATE_REGEX = r'(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$'
STATION_DATE_REGEX = r'(?P<station_number>\d+)/' + DATE_REGEX


maps_patterns = [
    path('', views.stations_on_map, name="stations_on_map"),
    re_path(r'^(?P<country>[a-zA-Z \-]+)/$', views.stations_on_map, name="stations_on_map"),
    re_path(r'^(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/$', views.stations_on_map, name="stations_on_map"),
    re_path(r'^(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/(?P<subcluster>[a-zA-Z \-]+)/$', views.stations_on_map, name="stations_on_map"),
]

network_patterns = [
    path('coincidences/', views.LatestNetworkSummaryRedirectView.as_view(), name="coincidences"),
    re_path(r'^coincidences/' + DATE_REGEX, views.NetworkSummaryDetailView.as_view(), name="coincidences"),
]

station_patterns = [
    path('<int:station_number>/', views.LatestSummaryRedirectView.as_view(), name="summary"),
    re_path(r'^' + STATION_DATE_REGEX, views.SummaryDetailView.as_view(), name="summary"),
    path('<int:station_number>/status/', views.station_status, name="status"),
    path('<int:station_number>/config/', views.station_config, name="config"),
    path('<int:station_number>/latest/', views.station_latest, name="latest"),
]

source_patterns = [
    # Network histograms
    re_path(fr'^{type}/' + DATE_REGEX, views.get_specific_network_histogram_source, {'type': type}, name=type)
    for type in ['coincidencetime', 'coincidencenumber']
] + [
    # Histograms
    re_path(fr'^{type}/' + STATION_DATE_REGEX, views.get_specific_histogram_source, {'type': type}, name=type)
    for type in ['eventtime', 'pulseheight', 'pulseintegral', 'singleslow', 'singleshigh', 'zenith', 'azimuth']
] + [
    # Datasets
    re_path(fr'^{type}/' + STATION_DATE_REGEX, views.get_specific_dataset_source, {'type': type}, name=type)
    for type in ['barometer', 'temperature', 'singlesratelow', 'singlesratehigh']
] + [
    # Configurations
    re_path(fr'^{type}/(?P<station_number>\d+)/$', views.get_specific_config_source, {'type': type}, name=type)
    for type in ['electronics', 'voltage', 'current', 'gps', 'trigger']
] + [
    # Histograms
    path('eventtime/<int:station_number>/', views.get_eventtime_source, name='eventtime'),

    # Configurations
    path('layout/<int:station_number>/', views.get_station_layout_source, name='layout'),

    # Calibrations
    path('detector_timing_offsets/<int:station_number>/', views.get_detector_timing_offsets_source, name="detector_offsets"),
    path('station_timing_offsets/<int:ref_station_number>/<int:station_number>/', views.get_station_timing_offsets_source, name="station_offsets"),
]

app_name = 'status'
urlpatterns = [
    path('stations/', views.stations, name="stations"),
    path('stations_by_country/', views.stations_by_country, name="stations_by_country"),
    path('stations_by_name/', views.stations_by_name, name="stations_by_name"),
    path('stations_by_number/', views.stations_by_number, name="stations_by_number"),
    path('stations_by_status/', views.stations_by_status, name="stations_by_status"),

    re_path(r'^stations_on_map/', include((maps_patterns, 'map'))),
    re_path(r'^network/', include((network_patterns, 'network'))),
    re_path(r'^stations/', include((station_patterns, 'station'))),
    re_path(r'^source/', include((source_patterns, 'source'))),

    path('help/', views.help, name="help"),
]
