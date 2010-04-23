from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.analysissessions',
    (r'^(?P<slug>[\w-]+)/data/$', 'views.data_display'),
    (r'^gateway/$', 'amfgateway.public_gateway'),
)
