from django.contrib import admin
from models import *

class GeneratorStateAdmin(admin.ModelAdmin):
    list_display = ('check_last_run', 'check_is_running', 'update_last_run',
                    'update_is_running')

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'needs_update', 'number_of_events')
    list_filter = ('station', 'needs_update', 'date')

admin.site.register(Summary, SummaryAdmin)
admin.site.register(DailyHistogram)
admin.site.register(HistogramType)
admin.site.register(GeneratorState, GeneratorStateAdmin)
