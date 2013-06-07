from django.conf.urls import patterns

urlpatterns = patterns('django_publicdb.analysissessions',
   (r'^(?P<slug>[\w-]+)/data/$', 'views.data_display'),
   (r'^request/(\w{20})/$','views.confirm_request'),
   (r'^request/create','views.create_request'),
   (r'^request/$', 'views.get_request'))
