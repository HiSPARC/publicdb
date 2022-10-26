from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'data'
urlpatterns = [
    path('', RedirectView.as_view(url='download', permanent=False)),
    path('download/', views.download_form, name="download_form"),
    path('download/<int:station_number>/<str:start>/<str:end>/', views.download_form, name="download_form"),
    path('download/coincidences/', views.coincidences_download_form, name="coincidences_download_form"),
    path(
        'download/coincidences/<str:start>/<str:end>/',
        views.coincidences_download_form,
        name="coincidences_download_form",
    ),
    path('rpc', views.call_xmlrpc, name="rpc"),
    path('<int:station_number>/events/', views.download_data, {'data_type': 'events'}, name="events"),
    path('<int:station_number>/weather/', views.download_data, {'data_type': 'weather'}, name="weather"),
    path('<int:station_number>/singles/', views.download_data, {'data_type': 'singles'}, name="singles"),
    path(
        'knmi/lightning/<int:lightning_type>/',
        views.download_data,
        {'data_type': 'lightning'},
        name="lightning",
    ),
    path('network/coincidences/', views.download_coincidences, name="coincidences"),
]
