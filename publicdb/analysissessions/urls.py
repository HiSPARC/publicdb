from django.conf.urls import url

from . import views

app_name = 'sessions'
urlpatterns = [
    url(r'^(?P<slug>[a-zA-Z0-9-]+)/data/$', views.data_display, name="data_display"),

    url(r'^request/$', views.request_form, name="request"),
    url(r'^request/validate$', views.validate_request_form, name="validate"),
    url(r'^request/(?P<url>[a-zA-Z0-9]{20})/$', views.confirm_request, name="confirm"),

    url(r'^get_coincidence/$', views.get_coincidence, name="get_coincidence"),
    url(r'^result/$', views.result, name="result"),
]
