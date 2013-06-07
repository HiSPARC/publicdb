from django.conf.urls import patterns

urlpatterns = patterns('django_publicdb.updates',
    (r'^(?P<queue>\w+)/check$', 'views.update_check_querystring'),
    (r'^(?P<queue>\w+)/check/(?P<admin_version>\d+)/(?P<user_version>\d+)/$', 'views.update_check'),
)
