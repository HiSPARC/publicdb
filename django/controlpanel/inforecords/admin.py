from django.contrib import admin
from models import *

class ContactAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'contactposition', 'email', 'phone_work', 'url')
    list_filter = ('contactposition',)
    ordering = ('last_name', 'first_name')

class OrganizationAdmin(admin.ModelAdmin):
    ordering = ('name',)

class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    ordering = ('country', 'name')

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'cluster')
    list_filter = ('cluster',)
    ordering = ('name',)

class StationAdmin(admin.ModelAdmin):
    list_display = ('number', 'location', 'cluster')
    ordering = ('number',)

class DetectorHisparcAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'status')
    ordering = ('station',)

class PcAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'ip','urlGenereer','certificaatGenereer')
    ordering = ('name',)

class PcMonitorServiceAdmin(admin.ModelAdmin):
    list_display = ('pc','monitor_service')
    ordering = ('pc','monitor_service')

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
admin.site.register(Electronics)
admin.site.register(PcType)
admin.site.register(Pc, PcAdmin)
admin.site.register(MonitorService)
admin.site.register(PcMonitorService, PcMonitorServiceAdmin)
