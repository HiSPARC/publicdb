from django.conf.urls import patterns

urlpatterns = patterns(
    'django_publicdb.inforecords.views',
    
    (r'^submit/$', 'submit_position')
)
