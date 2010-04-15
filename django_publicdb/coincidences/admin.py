from django.contrib import admin
from models import *


class EventAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'time', 'nanoseconds')

class CoincidenceAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'nanoseconds', 'num_events')


admin.site.register(Event, EventAdmin)
admin.site.register(Coincidence, CoincidenceAdmin)
