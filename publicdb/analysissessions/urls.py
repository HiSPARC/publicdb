from django.conf.urls import url

from . import views

app_name = 'sessions'
urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/data/$', views.data_display, name="data_display"),

    url(r'^request/$', views.request_form, name="request"),
    url(r'^request/validate$', views.validate_request_form, name="validate"),
    url(r'^request/(\w{20})/$', views.confirm_request, name="confirm"),
    url(r'^request/create', views.create_session, name="create"),
]
