from django.conf.urls import patterns

urlpatterns = patterns('django_publicdb.jsparc.views',
    (r'^get_coincidence/$', 'get_coincidence'),
    (r'^result/$', 'result'),
)
