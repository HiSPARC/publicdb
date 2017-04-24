from django.conf.urls import url

from . import views

app_name = 'sessions'
urlpatterns = [
    url(r'^get_coincidence/$', views.get_coincidence),
    url(r'^result/$', views.result),
]
