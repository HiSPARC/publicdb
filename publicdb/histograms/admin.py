from django.contrib import admin

from . import models


@admin.register(models.GeneratorState)
class GeneratorStateAdmin(admin.ModelAdmin):
    list_display = ('check_last_run', 'check_is_running', 'update_last_run',
                    'update_is_running')


@admin.register(models.NetworkHistogram)
class NetworkHistogramAdmin(admin.ModelAdmin):
    list_display = ('network_summary', 'type',)
    list_filter = ('type', 'network_summary__date',)
    raw_id_fields = ('network_summary',)


@admin.register(models.DailyHistogram, models.MultiDailyHistogram,
                models.DailyDataset, models.MultiDailyDataset)
class DailyStationDataAdmin(admin.ModelAdmin):
    list_display = ('summary', 'type',)
    list_filter = ('type', 'summary__station__number',)
    raw_id_fields = ('summary',)


class DailyHistogramInline(admin.StackedInline):
    model = models.DailyHistogram
    extra = 0


class MultiDailyHistogramInline(admin.StackedInline):
    model = models.MultiDailyHistogram
    extra = 0


class DailyDatasetInline(admin.StackedInline):
    model = models.DailyDataset
    extra = 0


class MultiDailyDatasetInline(admin.StackedInline):
    model = models.MultiDailyDataset
    extra = 0


class NetworkHistogramInline(admin.StackedInline):
    model = models.NetworkHistogram
    extra = 0


@admin.register(models.NetworkSummary)
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


@admin.register(models.Summary)
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
    inlines = (DailyHistogramInline, MultiDailyHistogramInline,
               DailyDatasetInline, MultiDailyDatasetInline)
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


@admin.register(models.Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('station', 'master', 'slave', 'timestamp')
    list_filter = ('timestamp', 'summary__station__number')
    raw_id_fields = ('summary',)


@admin.register(models.PulseheightFit)
class PulseheightFitAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'plate', 'fitted_mpv')
    list_filter = ('summary__station__number', 'plate', 'summary__date')
    raw_id_fields = ('summary',)


@admin.register(models.DetectorTimingOffset)
class DetectorTimingOffsetAdmin(admin.ModelAdmin):
    list_display = ('summary', 'offset_1', 'offset_2', 'offset_3', 'offset_4')
    list_filter = ('summary__station__number',)
    raw_id_fields = ('summary',)


@admin.register(models.StationTimingOffset)
class StationTimingOffsetAdmin(admin.ModelAdmin):
    list_display = ('ref_summary', 'summary', 'offset', 'error')
    list_filter = ('ref_summary__station__number', 'summary__station__number',
                   'ref_summary__date')
    raw_id_fields = ('ref_summary', 'summary')


admin.site.register(models.HistogramType)
admin.site.register(models.DatasetType)
