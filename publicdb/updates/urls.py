from django.conf.urls import url

from . import views

app_name = 'updates'
urlpatterns = [
    url(r'^installer/latest/$', views.get_latest_installer),
    url(r'^(?P<queue>\w+)/check$', views.update_check_querystring),
    url(r'^(?P<queue>\w+)/check/(?P<admin_version>\d+)/(?P<user_version>\d+)/?$', views.update_check),
]
