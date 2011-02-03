from django.conf.urls.defaults import url, patterns
from django.contrib import admin
from models import *
from django.utils.encoding import force_unicode
from django.utils.functional import update_wrapper
from forms import *

class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'prefix_surname', 'surname',
                    'email_work_link')

    def email_work_link(self, obj):
        return "<a href='mailto:%s'>%s</a>" % (obj.email_work,
                                               obj.email_work)
    email_work_link.allow_tags = True

admin.site.register(Profession)
admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactInformation)
admin.site.register(Cluster)
admin.site.register(Station)
admin.site.register(Country)
admin.site.register(DetectorHisparc)
admin.site.register(ElectronicsType)
admin.site.register(ElectronicsStatus)
admin.site.register(ElectronicsBatch)
admin.site.register(Electronics)
admin.site.register(PcType)
admin.site.register(Pc)
admin.site.register(MonitorService)
admin.site.register(EnabledService)
