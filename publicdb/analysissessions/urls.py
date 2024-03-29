from django.urls import path

from . import views

app_name = 'sessions'
urlpatterns = [
    path('<slug:slug>/data/', views.data_display, name='data_display'),
    path('get_coincidence/', views.get_coincidence, name='get_coincidence'),
    path('result/', views.result, name='result'),
]
