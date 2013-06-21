from django.contrib import admin
from models import *


class GeneratorStateAdmin(admin.ModelAdmin):
    list_display = ('check_last_run', 'check_is_running', 'update_last_run',
                    'update_is_running')


class DailyHistogramAdmin(admin.ModelAdmin):
    list_filter = ('type',)
    raw_id_fields = ('source',)


class DailyDatasetAdmin(admin.ModelAdmin):
    list_filter = ('type',)
    raw_id_fields = ('source',)


class DailyHistogramInline(admin.StackedInline):
    model = DailyHistogram
    extra = 0


class SummaryAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'needs_update',
                    'needs_update_events', 'needs_update_config',
                    'needs_update_errors', 'needs_update_weather',
                    'num_events', 'num_config', 'num_errors', 'num_weather')
    list_filter = ('station', 'needs_update', 'date')
    list_editable = ('needs_update',)
    inlines = (DailyHistogramInline,)


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('station', 'master', 'slave', 'timestamp')
    list_filter = ('timestamp', 'source__station__number')
    raw_id_fields = ('source',)


class PulseheightFitAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'plate', 'fitted_mpv')
    list_filter = ('source__station__number', 'plate', 'source__date')
    raw_id_fields = ('source',)


admin.site.register(GeneratorState, GeneratorStateAdmin)
admin.site.register(Summary, SummaryAdmin)
admin.site.register(DailyHistogram, DailyHistogramAdmin)
admin.site.register(HistogramType)
admin.site.register(DailyDataset, DailyDatasetAdmin)
admin.site.register(DatasetType)
admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(PulseheightFit, PulseheightFitAdmin)
