from django.urls import path, register_converter

from .. import converters
from . import views

register_converter(converters.YearConverter, 'year')
register_converter(converters.MonthConverter, 'month')
register_converter(converters.DateConverter, 'date')

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
    path('stations/data/<year:year>/', views.stations_with_data, {'type': 'events'}, name="data_stations"),
    path(
        'stations/data/<year:year>/<month:month>/',
        views.stations_with_data,
        {'type': 'events'},
        name="data_stations",
    ),
    path('stations/data/<date:date>/', views.stations_with_data, {'type': 'events'}, name="data_stations"),
    path('stations/weather/', views.stations_with_data, {'type': 'weather'}, name="weather_stations"),
    path(
        'stations/weather/<year:year>/',
        views.stations_with_data,
        {'type': 'weather'},
        name="weather_stations",
    ),
    path(
        'stations/weather/<year:year>/<month:month>/',
        views.stations_with_data,
        {'type': 'weather'},
        name="weather_stations",
    ),
    path(
        'stations/weather/<date:date>/',
        views.stations_with_data,
        {'type': 'weather'},
        name="weather_stations",
    ),
    path('stations/singles/', views.stations_with_data, {'type': 'singles'}, name="singles_stations"),
    path(
        'stations/singles/<year:year>/',
        views.stations_with_data,
        {'type': 'singles'},
        name="singles_stations",
    ),
    path(
        'stations/singles/<year:year>/<month:month>/',
        views.stations_with_data,
        {'type': 'singles'},
        name="singles_stations",
    ),
    path(
        'stations/singles/<date:date>/',
        views.stations_with_data,
        {'type': 'singles'},
        name="singles_stations",
    ),
    path('station/<int:station_number>/', views.station, name="station"),
    path('station/<int:station_number>/<date:date>/', views.station, name="station"),
    path('station/<int:station_number>/data/', views.has_data, {'type': 'events'}, name="has_data"),
    path('station/<int:station_number>/data/<year:year>/', views.has_data, {'type': 'events'}, name="has_data"),
    path(
        'station/<int:station_number>/data/<year:year>/<month:month>/',
        views.has_data,
        {'type': 'events'},
        name="has_data",
    ),
    path('station/<int:station_number>/data/<date:date>/', views.has_data, {'type': 'events'}, name="has_data"),
    path('station/<int:station_number>/weather/', views.has_data, {'type': 'weather'}, name="has_weather"),
    path(
        'station/<int:station_number>/weather/<year:year>/',
        views.has_data,
        {'type': 'weather'},
        name="has_weather",
    ),
    path(
        'station/<int:station_number>/weather/<year:year>/<month:month>/',
        views.has_data,
        {'type': 'weather'},
        name="has_weather",
    ),
    path(
        'station/<int:station_number>/weather/<date:date>/',
        views.has_data,
        {'type': 'weather'},
        name="has_weather",
    ),
    path('station/<int:station_number>/singles/', views.has_data, {'type': 'singles'}, name="has_singles"),
    path(
        'station/<int:station_number>/singles/<year:year>/',
        views.has_data,
        {'type': 'singles'},
        name="has_singles",
    ),
    path(
        'station/<int:station_number>/singles/<year:year>/<month:month>/',
        views.has_data,
        {'type': 'singles'},
        name="has_singles",
    ),
    path(
        'station/<int:station_number>/singles/<date:date>/',
        views.has_data,
        {'type': 'singles'},
        name="has_singles",
    ),
    path('station/<int:station_number>/config/', views.config, name="config"),
    path('station/<int:station_number>/config/<date:date>/', views.config, name="config"),
    path('station/<int:station_number>/num_events/', views.num_events, name="num_events"),
    path('station/<int:station_number>/num_events/<year:year>/', views.num_events, name="num_events"),
    path(
        'station/<int:station_number>/num_events/<year:year>/<month:month>/',
        views.num_events,
        name="num_events",
    ),
    path('station/<int:station_number>/num_events/<date:date>/', views.num_events, name="num_events"),
    path('station/<int:station_number>/num_events/<date:date>/<int:hour>/', views.num_events, name="num_events"),
    path('station/<int:station_number>/trace/<int:ext_timestamp>/', views.get_event_traces, name="event_traces"),
]
