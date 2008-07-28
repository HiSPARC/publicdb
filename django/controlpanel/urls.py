from django.conf.urls.defaults import *
from inforecords.views import *


urlpatterns = patterns('',
    # Example:
     (r'^certificaat/genereer/(.+)/(.+).zip$', genereer),
     (r'^maakconfig$', maakconfig),
    # Uncomment this for admin:
     (r'^$', indexpagina),
     (r'^admin/', include('django.contrib.admin.urls')),
)
