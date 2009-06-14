from django_publicdb.coincidences.models import Coincidence, Event
from django.contrib import admin

    
class CoincidenceAdmin(admin.ModelAdmin):
    list_display = ('id','date','time','nanoseconds','nevents','event_ids','nodouble','intime')
    fieldsets = [
                (None,      {'fields':['date','time','nanoseconds']}),
                ('Events',  {'fields':['nevents','nodouble','intime']})
                ]
    list_filter = ['date']
    date_hierarchy = 'date'


class EventAdmin(admin.ModelAdmin):
    list_display = ('event_id','date','time','nanoseconds')
    fieldsets = [
        (None,              {'fields': ['event_id','date','time','nanoseconds','detector']}),
        ('Location',        {'fields': ['latitude','longitude','height']}),
        ('Pulse heights',   {'fields': ['pulseheight1','pulseheight2','pulseheight3','pulseheight4']}),
        ('Integrals',       {'fields': ['integral1','integral2','integral3','integral4']}),
        ('Traces',          {'fields': ['trace1','trace2','trace3','trace4'], 'classes': ['collapse']})
        ]
    list_filter = ['date']
    date_hierarchy = 'date'


admin.site.register(Coincidence, CoincidenceAdmin)
admin.site.register(Event, EventAdmin)
