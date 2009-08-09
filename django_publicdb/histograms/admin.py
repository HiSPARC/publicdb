from django.contrib import admin
from models import *

class GeneratorStateAdmin(admin.ModelAdmin):
    list_display = ('check_last_run', 'check_is_running', 'update_last_run',
                    'update_is_running', 'last_event_id')

class DailyHistogramInline(admin.StackedInline):
    model = DailyHistogram
    extra = 0

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('station_id', 'date', 'needs_update', 'has_raw_data')
    list_filter = ('station_id', 'date', 'needs_update', 'has_raw_data')
    inlines = (DailyHistogramInline,)

admin.site.register(GeneratorState, GeneratorStateAdmin)
admin.site.register(Summary, SummaryAdmin)
admin.site.register(DailyHistogram)
admin.site.register(HistogramType)
