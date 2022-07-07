from django.urls import path, re_path

from . import views

app_name = 'maps'
urlpatterns = [
    path('', views.stations_on_map, name="map"),
    path('<int:station_number>/', views.station_on_map, name="map"),
    re_path(r'^(?P<country>[a-zA-Z \-]+)/$', views.stations_on_map, name="map"),
    re_path(r'^(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/$', views.stations_on_map, name="map"),
    re_path(r'^(?P<country>[a-zA-Z \-]+)/(?P<cluster>[a-zA-Z \-]+)/(?P<subcluster>[a-zA-Z \-]+)/$', views.stations_on_map, name="map"),
]
