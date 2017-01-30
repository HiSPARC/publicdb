from django.conf.urls import patterns

urlpatterns = patterns('django_publicdb.live.views',
    (r'^stations/(?P<station_id>\d+)/$', 'station'),
    (r'^event/(?P<station_id>\d+)/$', 'get_new_event'),
    (r'^event/(?P<station_id>\d+)/(?P<iterator>\d+)/$', 'get_new_event'),
)
