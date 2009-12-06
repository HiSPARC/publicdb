from django.contrib import admin
from models import *

class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'prefix_last_name', 'last_name',
                    'contactposition', 'location', 'email', 'phone_work')
    list_display_links = ('first_name', 'prefix_last_name', 'last_name')
    list_filter = ('contactposition', 'location')

class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)

class StationInline(admin.StackedInline):
    model = Station
    extra = 1

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'cluster')
    list_filter = ('cluster',)
    inlines = (StationInline,)

class LocationInline(admin.StackedInline):
    model = Location
    extra = 1

class StationAdmin(admin.ModelAdmin):
    list_display = ('number', 'location', 'cluster')
    search_fields = ('number', 'location__name', 'location__cluster__name')

class DetectorHisparcAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'status')
    list_filter = ('status',)

class ElectronicsAdmin(admin.ModelAdmin):
    list_filter = ('batch',)

class OrganizationAdmin(admin.ModelAdmin):
    inlines = (LocationInline,)

class EnabledServiceAdmin(admin.ModelAdmin):
    list_display = ('pc', 'monitor_service', 'min_critical', 'max_critical',
                    'min_warning', 'max_warning')
    list_filter = ('pc', 'monitor_service')

class EnabledServiceInline(admin.TabularInline):
    model = EnabledService
    extra = 10

class PcAdmin(admin.ModelAdmin):
    list_display = ('station', 'name', 'is_active', 'type', 'ip', 'url',
                    'certificaat')
    list_filter = ('is_active',)
    ordering = ('station',)
    inlines = (EnabledServiceInline,)

class MonitorServiceAdmin(admin.ModelAdmin):
    list_display = ('description', 'is_default_service', 'nagios_command')
    inlines = (EnabledServiceInline,)

admin.site.register(Contactposition)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Cluster, ClusterAdmin)
admin.site.register(LocationStatus)
admin.site.register(Location, LocationAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(DetectorStatus)
admin.site.register(DetectorHisparc, DetectorHisparcAdmin)
admin.site.register(ElectronicsType)
admin.site.register(ElectronicsStatus)
admin.site.register(ElectronicsBatch)
admin.site.register(Electronics, ElectronicsAdmin)
admin.site.register(PcType)
admin.site.register(Pc, PcAdmin)
admin.site.register(MonitorService, MonitorServiceAdmin)
admin.site.register(EnabledService, EnabledServiceAdmin)
