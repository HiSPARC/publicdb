from django.conf.urls import patterns

urlpatterns = patterns('django_publicdb.station_layout.views',
    (r'^submit/$', 'submit_layout'),
    (r'^submitted/$', 'submitted_layout'),
    (r'^confirm/(?P<hash>\w{32})/$', 'confirmed_layout'),
    (r'^review/(?P<hash>\w{32})/$', 'review_layout'),
)
