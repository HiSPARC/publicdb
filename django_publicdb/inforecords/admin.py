from django.conf.urls.defaults import url, patterns
from django.contrib import admin
from models import *
from django.utils.encoding import force_unicode
from django.utils.functional import update_wrapper
from forms import *

class ClusterAdmin(admin.ModelAdmin):
	def get_urls(self):
		def wrap(view):
			def wrapper(*args, **kwds):
				kwds['admin'] = self
				return self.admin_site.admin_view(view)(*args, **kwds)
			return update_wrapper(wrapper, view)
		urlpatterns = patterns('',
			url(r'^wizard/$',
				wrap(create_cluster),
				name='inforecords_cluster_add')
		)
		urlpatterns += super(ClusterAdmin, self).get_urls()
		return urlpatterns

admin.site.register(Cluster, ClusterAdmin)
admin.site.register(Profession)
admin.site.register(Contact)
admin.site.register(Contact_Information)
#admin.site.register(Cluster)
admin.site.register(Station)
admin.site.register(Country)
admin.site.register(DetectorStatus)
admin.site.register(DetectorHisparc)
admin.site.register(ElectronicsType)
admin.site.register(ElectronicsStatus)
admin.site.register(ElectronicsBatch)
admin.site.register(Electronics)
admin.site.register(PcType)
admin.site.register(Pc)
admin.site.register(MonitorService)
admin.site.register(EnabledService)
