from django.urls import path, re_path

from . import views

app_name = 'api'
urlpatterns = [
    path('', views.man, name="man"),

    path('network/status/', views.network_status),

    path('stations/', views.stations, name="stations"),
    path('subclusters/', views.subclusters, name="subclusters"),
    path('clusters/', views.clusters, name="clusters"),
    path('countries/', views.countries, name="countries"),

    path('subclusters/<int:subcluster_number>/', views.stations, name="stations"),
    path('clusters/<int:cluster_number>/', views.subclusters, name="subclusters"),
    path('countries/<int:country_number>/', views.clusters, name="clusters"),

    path('stations/data/', views.stations_with_data, {'type': 'events'}, name="data_stations"),
    re_path(r'^stations/data/(?P<year>\d{4})/$', views.stations_with_data, {'type': 'events'}, name="data_stations"),
    re_path(r'^stations/data/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.stations_with_data, {'type': 'events'}, name="data_stations"),
    re_path(r'^stations/data/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', views.stations_with_data, {'type': 'events'}, name="data_stations"),
    path('stations/weather/', views.stations_with_data, {'type': 'weather'}, name="weather_stations"),
    re_path(r'^stations/weather/(?P<year>\d{4})/$', views.stations_with_data, {'type': 'weather'}, name="weather_stations"),
    re_path(r'^stations/weather/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.stations_with_data, {'type': 'weather'}, name="weather_stations"),
    re_path(r'^stations/weather/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', views.stations_with_data, {'type': 'weather'}, name="weather_stations"),
    path('stations/singles/', views.stations_with_data, {'type': 'singles'}, name="singles_stations"),
    re_path(r'^stations/singles/(?P<year>\d{4})/$', views.stations_with_data, {'type': 'singles'}, name="singles_stations"),
    re_path(r'^stations/singles/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.stations_with_data, {'type': 'singles'}, name="singles_stations"),
    re_path(r'^stations/singles/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', views.stations_with_data, {'type': 'singles'}, name="singles_stations"),

    path('station/<int:station_number>/', views.station, name="station"),
    re_path(r'^station/(?P<station_number>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', views.station, name="station"),

    path('station/<int:station_number>/data/', views.has_data, {'type': 'events'}, name="has_data"),
    re_path(r'^station/(?P<station_number>\d+)/data/(?P<year>\d{4})/$', views.has_data, {'type': 'events'}, name="has_data"),
    re_path(r'^station/(?P<station_number>\d+)/data/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.has_data, {'type': 'events'}, name="has_data"),
    re_path(r'^station/(?P<station_number>\d+)/data/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', views.has_data, {'type': 'events'}, name="has_data"),
    path('station/<int:station_number>/weather/', views.has_data, {'type': 'weather'}, name="has_weather"),
    re_path(r'^station/(?P<station_number>\d+)/weather/(?P<year>\d{4})/$', views.has_data, {'type': 'weather'}, name="has_weather"),
    re_path(r'^station/(?P<station_number>\d+)/weather/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.has_data, {'type': 'weather'}, name="has_weather"),
    re_path(r'^station/(?P<station_number>\d+)/weather/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', views.has_data, {'type': 'weather'}, name="has_weather"),
    path('station/<int:station_number>/singles/', views.has_data, {'type': 'singles'}, name="has_singles"),
    re_path(r'^station/(?P<station_number>\d+)/singles/(?P<year>\d{4})/$', views.has_data, {'type': 'singles'}, name="has_singles"),
    re_path(r'^station/(?P<station_number>\d+)/singles/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.has_data, {'type': 'singles'}, name="has_singles"),
    re_path(r'^station/(?P<station_number>\d+)/singles/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', views.has_data, {'type': 'singles'}, name="has_singles"),
    path('station/<int:station_number>/config/', views.config, name="config"),
    re_path(r'^station/(?P<station_number>\d+)/config/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', views.config, name="config"),

    path('station/<int:station_number>/num_events/', views.num_events, name="num_events"),
    re_path(r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/$', views.num_events, name="num_events"),
    re_path(r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.num_events, name="num_events"),
    re_path(r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', views.num_events, name="num_events"),
    re_path(r'^station/(?P<station_number>\d+)/num_events/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<hour>\d+)/$', views.num_events, name="num_events"),

    path('station/<int:station_number>/trace/<int:ext_timestamp>/', views.get_event_traces, name="event_traces"),
]
