from django.contrib import admin

from .models import (Configuration, DailyDataset, DailyHistogram, DatasetType,
                     DetectorTimingOffset, GeneratorState, HistogramType,
                     NetworkHistogram, NetworkSummary, PulseheightFit,
                     StationTimingOffset, Summary)


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
    list_filter = ('needs_update', 'needs_update_coincidences', 'date')
    list_editable = ('needs_update', 'needs_update_coincidences')
    inlines = (NetworkHistogramInline,)
    list_per_page = 200
    actions = ['unset_update_flag', 'unset_coincidences_flag',
               'set_update_flag', 'set_coincidences_flag']

    def unset_update_flag(self, request, qs):
        qs.update(needs_update=False)
    unset_update_flag.short_description = "Unset needs_update"

    def unset_coincidences_flag(self, request, qs):
        qs.update(needs_update_coincidences=False)
    unset_coincidences_flag.short_description = ("Unset "
                                                 "needs_update_coincidences")

    def set_update_flag(self, request, qs):
        qs.update(needs_update=True)
    set_update_flag.short_description = "Set needs_update"

    def set_coincidences_flag(self, request, qs):
        """Only set flags if num coincidences is not null"""
        (qs.filter(num_coincidences__isnull=False)
           .update(needs_update_coincidences=True))
    set_coincidences_flag.short_description = "Set needs_update_coincidences"


class SummaryAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'num_events', 'num_config',
                    'num_errors', 'num_weather', 'num_singles',
                    'needs_update', 'needs_update_events',
                    'needs_update_config', 'needs_update_errors',
                    'needs_update_weather', 'needs_update_singles')
    list_filter = ('station', 'needs_update', 'needs_update_events',
                   'needs_update_weather', 'needs_update_singles',
                   'needs_update_config', 'date')
    list_editable = ('needs_update', 'needs_update_events',
                     'needs_update_weather', 'needs_update_singles',
                     'needs_update_config')
    inlines = (DailyHistogramInline,)
    list_per_page = 200
    actions = ['unset_update_flag', 'unset_events_flag', 'unset_config_flag',
               'set_update_flag', 'set_events_flag', 'set_config_flag']

    def unset_update_flag(self, request, qs):
        qs.update(needs_update=False)
    unset_update_flag.short_description = "Unset needs_update"

    def unset_events_flag(self, request, qs):
        qs.update(needs_update_events=False)
    unset_events_flag.short_description = "Unset needs_update_events"

    def unset_config_flag(self, request, qs):
        qs.update(needs_update_config=False)
    unset_config_flag.short_description = "Unset needs_update_config"

    def set_update_flag(self, request, qs):
        qs.update(needs_update=True)
    set_update_flag.short_description = "Set needs_update"

    def set_events_flag(self, request, qs):
        """Only set flags if num events is not null"""
        qs.filter(num_events__isnull=False).update(needs_update_events=True)
    set_events_flag.short_description = "Set needs_update_events"

    def set_config_flag(self, request, qs):
        """Only set flags if num config is not null"""
        qs.filter(num_config__isnull=False).update(needs_update_config=True)
    set_config_flag.short_description = "Set needs_update_config"


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


class StationTimingOffsetAdmin(admin.ModelAdmin):
    list_display = ('ref_source', 'source', 'offset', 'error')
    list_filter = ('ref_source__station__number', 'source__station__number',
                   'ref_source__date')
    raw_id_fields = ('ref_source', 'source')


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
admin.site.register(StationTimingOffset, StationTimingOffsetAdmin)
