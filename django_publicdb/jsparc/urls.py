from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.jsparc.views',
    (r'^get_coincidence/$', 'get_coincidence'),
    (r'^result/$', 'result'),
)
