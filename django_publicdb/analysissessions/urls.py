from django.conf.urls import patterns

urlpatterns = patterns('django_publicdb.analysissessions.views',
    (r'^(?P<slug>[\w-]+)/data/$', 'data_display'),

    (r'^request/$', 'request_form'),
    (r'^request/validate$', 'validate_request_form'),
    (r'^request/(\w{20})/$', 'confirm_request'),
    (r'^request/create', 'create_session')
)
