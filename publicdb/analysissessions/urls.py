from django.urls import path

from . import views

app_name = 'sessions'
urlpatterns = [
    path('<slug:slug>/data/', views.data_display, name='data_display'),
    path('request/', views.request_form, name='request'),
    path('request/validate/', views.validate_request_form, name='validate'),
    path('request/<slug:url>/', views.confirm_request, name='confirm'),
    path('get_coincidence/', views.get_coincidence, name='get_coincidence'),
    path('result/', views.result, name='result'),
]
