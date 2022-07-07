from django.urls import path, re_path

from . import views

app_name = 'updates'
urlpatterns = [
    path('installer/latest/', views.get_latest_installer, name="latest"),
    re_path(r'^(?P<queue>[a-zA-Z0-9_]+)/check$', views.update_check_querystring, name="check"),
    re_path(r'^(?P<queue>[a-zA-Z0-9_]+)/check/(?P<admin_version>\d+)/(?P<user_version>\d+)/?$', views.update_check, name="check"),
]
