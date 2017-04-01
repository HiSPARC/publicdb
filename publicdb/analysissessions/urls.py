from django.conf.urls import url

from . import views

urlpatterns = [
    (r'^(?P<slug>[\w-]+)/data/$', views.data_display),

    (r'^request/$', views.request_form),
    (r'^request/validate$', views.validate_request_form),
    (r'^request/(\w{20})/$', views.confirm_request),
    (r'^request/create', views.create_session),
]
