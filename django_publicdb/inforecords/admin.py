from django.conf.urls.defaults import url, patterns
from django.contrib import admin
from models import *
from django.utils.encoding import force_unicode
from django.utils.functional import update_wrapper
from forms import *

admin.site.register(Profession)
admin.site.register(Contact)
admin.site.register(Contact_Information)
admin.site.register(Cluster)
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
