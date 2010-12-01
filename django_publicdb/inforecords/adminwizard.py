from django.contrib.admin.sites import *
from django.conf.urls.defaults import url, patterns
from django.contrib import admin
from models import *
from django.utils.encoding import force_unicode
from django.utils.functional import update_wrapper
from forms import *

adminwizard=AdminSite(name='adminwizard')

class SubClusterAdmin(admin.ModelAdmin):
	def get_urls(self):
		def wrap(view):
			def wrapper(*args, **kwds):
				kwds['admin'] = self
				return self.admin_site.admin_view(view)(*args, **kwds)
			return update_wrapper(wrapper, view)
		urlpatterns = patterns('',
			url(r'^add/$',
				wrap(create_subcluster),
				name='inforecords_subcluster_add')
		)
		urlpatterns += super(SubClusterAdmin, self).get_urls()
		return urlpatterns

class StationAdmin(admin.ModelAdmin):
        def get_urls(self):
                def wrap(view):
                        def wrapper(*args, **kwds):
                                kwds['admin'] = self
                                return self.admin_site.admin_view(view)(*args, **kwds)
                        return update_wrapper(wrapper, view)
                urlpatterns = patterns('',
                        url(r'^add/$',
                                wrap(create_station),
                                name='inforecords_station_add')
                )
                urlpatterns += super(StationAdmin, self).get_urls()
                return urlpatterns

class ContactAdmin(admin.ModelAdmin):
        def get_urls(self):
                def wrap(view):
                        def wrapper(*args, **kwds):
                                kwds['admin'] = self
                                return self.admin_site.admin_view(view)(*args, **kwds)
                        return update_wrapper(wrapper, view)
                urlpatterns = patterns('',
                        url(r'^add/$',
                                wrap(create_contact),
                                name='inforecords_contact_add')
                )
                urlpatterns += super(ContactAdmin, self).get_urls()
                return urlpatterns

adminwizard.register(Cluster, SubClusterAdmin)
adminwizard.register(Station, StationAdmin)
adminwizard.register(Contact, ContactAdmin)
#wizardadmin.register(Contact)
#wizardadmin.register(Contact_Information)
