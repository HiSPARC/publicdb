from django.conf.urls.defaults import *

urlpatterns = patterns('django_publicdb.symposium2009',
    (r'^data/$', 'views.data_display'),
    (r'^gateway/$', 'amfgateway.public_gateway'),
)
