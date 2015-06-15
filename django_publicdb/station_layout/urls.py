from django.conf.urls import patterns

urlpatterns = patterns('django_publicdb.station_layout.views',
    (r'^submit/$', 'layout_submit'),
    (r'^submit/validate/$', 'validate_layout_submit'),
    (r'^confirm/(?P<hash>\w{32})/$', 'confirmed_layout'),
    (r'^review/(?P<hash>\w{32})/$', 'review_layout'),
    (r'^review/(?P<hash>\w{32})/validate/$', 'validate_review_layout'),
)
