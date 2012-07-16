from django.conf.urls.defaults import *

urlpatterns = patterns(
    'django_publicdb.analysissessions.views',
    ( r'^(?P<slug>[\w-]+)/data/$', 'data_display' ),

    ( r'^request/$',               'request_form' ),
    ( r'^request/validate$',       'validate_request_form' ),
    ( r'^request/create',          'create_request' ),
    ( r'^request/(\w{20})/$',      'confirm_request' )
)
