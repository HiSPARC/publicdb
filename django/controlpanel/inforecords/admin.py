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

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'cluster')
    list_filter = ('cluster',)

class StationAdmin(admin.ModelAdmin):
    list_display = ('number', 'location', 'cluster')

class DetectorHisparcAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'status')
    list_filter = ('status',)

class ElectronicsAdmin(admin.ModelAdmin):
    list_filter = ('batch',)

class PcAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'ip', 'url', 'certificaat')

class PcMonitorServiceAdmin(admin.ModelAdmin):
    list_display = ('pc','monitor_service')
    list_filter = ('pc',)

class MonitorServiceAdmin(admin.ModelAdmin):
    list_display = ('description', 'nagios_command')

admin.site.register(Contactposition)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Organization)
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
admin.site.register(PcMonitorService, PcMonitorServiceAdmin)
