from django.conf.urls.defaults import url, patterns
from django.contrib import admin
from models import *
from django.utils.encoding import force_unicode
from django.utils.functional import update_wrapper

class ClusterAdmin(admin.ModelAdmin):
    list_display = ('number','name', 'parent', 'country')
    list_filter = ('country',)

class ContactInline(admin.StackedInline):
    model = Contact
    extra = 0 #this stops empty forms being shown
    max_num = 0 #this removes the add more button
    can_delete = False

class StationInline(admin.StackedInline):
    model = Station
    extra = 0 #this stops empty forms being shown
    max_num = 0 #this removes the add more button
    can_delete = False

class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'prefix_surname', 'surname',
                    'email_work_link')

    def email_work_link(self, obj):
        return "<a href='mailto:%s'>%s</a>" % (obj.email_work,
                                               obj.email_work)
    email_work_link.allow_tags = True

class CountryAdmin(admin.ModelAdmin):
    list_display = ('number','name')
    ordering = ['number']

class ElectronicsAdmin(admin.ModelAdmin):
    list_filter = ('batch',)

class EnabledServiceAdmin(admin.ModelAdmin):
    list_display = ('pc', 'monitor_service', 'min_critical', 'max_critical',
                    'min_warning', 'max_warning')
    list_filter = ('pc', 'monitor_service')

class StationAdmin(admin.ModelAdmin):
    list_display = ('number','name', 'contactinformation', 'cluster')
    search_fields = ('number', 'name', 'cluster__name')

class ContactInformationAdmin(admin.ModelAdmin):
    def owner_name(self,obj):
       return obj.contact_owner
    list_display = ('owner_name','street_1','street_2','city','type')
    def type(self,obj):
       return obj.type
    inlines = (ContactInline,StationInline)

class EnabledServiceInline(admin.TabularInline):
    model = EnabledService
    extra = 10

class MonitorServiceAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_default_service', 'nagios_command')
    inlines = (EnabledServiceInline,)

class PcAdmin(admin.ModelAdmin):
    list_display = ('station', 'name', 'is_active', 'type', 'ip', 'url',
                    'keys')
    list_filter = ('is_active',)
    ordering = ('station',)
    inlines = (EnabledServiceInline,)

class ElectronicsAdmin(admin.ModelAdmin):
    list_filter = ('batch',)

class EnabledServiceAdmin(admin.ModelAdmin):
    list_display = ('pc', 'monitor_service', 'min_critical', 'max_critical',
                    'min_warning', 'max_warning')
    list_filter = ('pc', 'monitor_service')


admin.site.register(Profession)
admin.site.register(Contact,ContactAdmin)
admin.site.register(ContactInformation,ContactInformationAdmin)
admin.site.register(Cluster,ClusterAdmin)
admin.site.register(Station,StationAdmin)
admin.site.register(Country,CountryAdmin)
admin.site.register(DetectorHisparc)
admin.site.register(ElectronicsType)
admin.site.register(ElectronicsStatus)
admin.site.register(ElectronicsBatch)
admin.site.register(Electronics, ElectronicsAdmin)
admin.site.register(PcType)
admin.site.register(Pc, PcAdmin)
admin.site.register(MonitorService, MonitorServiceAdmin)
admin.site.register(EnabledService,EnabledServiceAdmin)
