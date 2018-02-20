from django.contrib import admin

from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'time', 'nanoseconds')


@admin.register(models.Coincidence)
class CoincidenceAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'nanoseconds', 'num_events')
    raw_id_fields = ('events',)
