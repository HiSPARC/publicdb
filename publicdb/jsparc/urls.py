from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get_coincidence/$', views.get_coincidence),
    url(r'^result/$', views.result),
]
