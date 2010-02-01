from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.symposium2009.views',
    (r'^data/$', 'data_display'),
)
