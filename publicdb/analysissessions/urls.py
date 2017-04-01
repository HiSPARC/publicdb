from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/data/$', views.data_display),

    url(r'^request/$', views.request_form),
    url(r'^request/validate$', views.validate_request_form),
    url(r'^request/(\w{20})/$', views.confirm_request),
    url(r'^request/create', views.create_session),
]
