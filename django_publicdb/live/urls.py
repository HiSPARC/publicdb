from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.live.views',
    (r'^stations/(?P<station_id>\d+)/$', 'station'),
)
