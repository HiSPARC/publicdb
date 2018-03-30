from django.contrib import admin

from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'time', 'nanoseconds')


class EventInline(admin.StackedInline):
    model = models.Event
    extra = 0


@admin.register(models.Coincidence)
class CoincidenceAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'nanoseconds', 'num_events')
    inlines = (EventInline,)
