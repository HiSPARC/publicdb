from django.urls import path, re_path

from . import views

app_name = 'sessions'
urlpatterns = [
    re_path(r'^(?P<slug>[a-zA-Z0-9-]+)/data/$', views.data_display, name="data_display"),

    path('request/', views.request_form, name="request"),
    path('request/validate', views.validate_request_form, name="validate"),
    re_path(r'^request/(?P<url>[a-zA-Z0-9]{20})/$', views.confirm_request, name="confirm"),

    path('get_coincidence/', views.get_coincidence, name="get_coincidence"),
    path('result/', views.result, name="result"),
]
