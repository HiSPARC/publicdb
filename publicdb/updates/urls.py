from django.conf.urls import url

from . import views

app_name = 'updates'
urlpatterns = [
    url(r'^installer/latest/$', views.get_latest_installer, name="latest"),
    url(r'^(?P<queue>[a-zA-Z0-9_]+)/check$', views.update_check_querystring, name="check"),
    url(r'^(?P<queue>[a-zA-Z0-9_]+)/check/(?P<admin_version>\d+)/(?P<user_version>\d+)/?$', views.update_check, name="check"),
]
