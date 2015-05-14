from django.contrib import admin

from .models import (GeneratorState, NetworkHistogram, DailyHistogram,
                     DailyDataset, NetworkSummary, Summary, Configuration,
                     PulseheightFit, HistogramType, DatasetType,
                     DetectorTimingOffset)


class GeneratorStateAdmin(admin.ModelAdmin):
    list_display = ('check_last_run', 'check_is_running', 'update_last_run',
                    'update_is_running')


class NetworkHistogramAdmin(admin.ModelAdmin):
    list_display = ('source', 'type',)
    list_filter = ('type', 'source__date',)
    raw_id_fields = ('source',)


class DailyHistogramAdmin(admin.ModelAdmin):
    list_display = ('source', 'type',)
    list_filter = ('type', 'source__station__number',)
    raw_id_fields = ('source',)


class DailyDatasetAdmin(admin.ModelAdmin):
    list_display = ('source', 'type',)
    list_filter = ('type', 'source__station__number',)
    raw_id_fields = ('source',)


class DailyHistogramInline(admin.StackedInline):
    model = DailyHistogram
    extra = 0


class NetworkHistogramInline(admin.StackedInline):
    model = NetworkHistogram
    extra = 0


class NetworkSummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'needs_update', 'needs_update_coincidences',
                    'num_coincidences',)
    list_filter = ('needs_update_coincidences', 'date')
    inlines = (NetworkHistogramInline,)


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


class DetectorTimingOffsetAdmin(admin.ModelAdmin):
    list_display = ('source', 'offset_1', 'offset_2', 'offset_3', 'offset_4')
    list_filter = ('source__station__number',)
    raw_id_fields = ('source',)


admin.site.register(GeneratorState, GeneratorStateAdmin)
admin.site.register(NetworkHistogram, NetworkHistogramAdmin)
admin.site.register(DailyHistogram, DailyHistogramAdmin)
admin.site.register(DailyDataset, DailyDatasetAdmin)
admin.site.register(NetworkSummary, NetworkSummaryAdmin)
admin.site.register(Summary, SummaryAdmin)
admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(PulseheightFit, PulseheightFitAdmin)
admin.site.register(HistogramType)
admin.site.register(DatasetType)
admin.site.register(DetectorTimingOffset, DetectorTimingOffsetAdmin)
