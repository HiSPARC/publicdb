from django.conf.urls import patterns

urlpatterns = patterns('django_publicdb.updates.views',
    (r'^installer/latest/$', 'get_latest_installer'),
    (r'^(?P<queue>\w+)/check$', 'update_check_querystring'),
    (r'^(?P<queue>\w+)/check/(?P<admin_version>\d+)/(?P<user_version>\d+)/$',
     'update_check'),
)
