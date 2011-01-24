from django.conf.urls.defaults import *
import django.views.generic.simple

urlpatterns = patterns('django_publicdb.ajax.views',
    (r'^data/$', 'data'),
    (r'^data_cors/$', 'data_cors'),
)
