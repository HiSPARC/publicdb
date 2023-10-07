from django.urls import path

from . import views

app_name = 'maps'
urlpatterns = [
    path('', views.stations_on_map, name='map'),
    path('<int:station_number>/', views.station_on_map, name='map'),
    path('<str:country>/', views.stations_on_map, name='map'),
    path('<str:country>/<str:cluster>/', views.stations_on_map, name='map'),
    path('<str:country>/<str:cluster>/<str:subcluster>/', views.stations_on_map, name='map'),
]
