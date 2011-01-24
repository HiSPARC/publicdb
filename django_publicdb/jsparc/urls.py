from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.jsparc.views',
    (r'^coin_cors/$', 'coin_cors'),
)
