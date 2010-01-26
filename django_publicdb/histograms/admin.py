from django.contrib import admin
from models import *

class GeneratorStateAdmin(admin.ModelAdmin):
    list_display = ('check_last_run', 'check_is_running', 'update_last_run',
                    'update_is_running')

class DailyHistogramInline(admin.StackedInline):
    model = DailyHistogram
    extra = 0

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'needs_update',
                    'needs_update_events', 'needs_update_config',
                    'needs_update_errors', 'num_events', 'num_config',
                    'num_errors')
    list_filter = ('station', 'needs_update', 'date')
    list_editable = ('needs_update',)
    inlines = (DailyHistogramInline,)

class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('station', 'timestamp')

admin.site.register(GeneratorState, GeneratorStateAdmin)
admin.site.register(Summary, SummaryAdmin)
admin.site.register(DailyHistogram)
admin.site.register(HistogramType)
admin.site.register(Configuration, ConfigurationAdmin)
