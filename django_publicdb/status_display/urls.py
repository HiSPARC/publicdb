from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.status_display.views',
    (r'^status/$', 'status'),
    (r'^stations/$', 'stations'),
    (r'^stations/(?P<station_id>\d+)/$', 'station'),
    (r'^stations/(?P<station_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$',
        'station_histograms'),
)
