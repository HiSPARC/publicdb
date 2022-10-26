import datetime
import re

from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

FIRSTDATE = datetime.date(2004, 1, 1)


class NetworkSummaryQuerySet(models.QuerySet):
    def valid_date(self):
        """Filter by date to dates between start and today"""
        return self.filter(date__gte=FIRSTDATE, date__lte=datetime.date.today())

    def with_coincidences(self):
        return self.valid_date().filter(num_coincidences__isnull=False)


class NetworkSummary(models.Model):
    date = models.DateField(unique=True)
    num_coincidences = models.IntegerField(blank=True, null=True)
    needs_update = models.BooleanField(default=False)
    needs_update_coincidences = models.BooleanField(default=False)

    objects = NetworkSummaryQuerySet.as_manager()

    def get_absolute_url(self):
        kwargs = {'date': self.date}
        return reverse('status:network:coincidences', kwargs=kwargs)

    def __str__(self):
        return f'Network Summary: {self.date}'

    class Meta:
        verbose_name = 'Network summary'
        verbose_name_plural = 'Network summaries'
        ordering = ['date']
        get_latest_by = 'date'


class SummaryQuerySet(models.QuerySet):
    def valid_date(self):
        """Filter by date to dates between start and today"""
        return self.filter(date__gte=FIRSTDATE, date__lte=datetime.date.today())

    def with_data(self):
        """Filter with at least either events or weather data"""
        return self.valid_date().filter(models.Q(num_events__isnull=False) | models.Q(num_weather__isnull=False))

    def with_events(self):
        """Filter with at least events"""
        return self.valid_date().filter(num_events__isnull=False)

    def with_config(self):
        """Filter with at least configurations"""
        return self.valid_date().filter(num_config__isnull=False)

    def with_events_in_last_hour(self):
        """Filter with events in last hour"""
        return self.valid_date().filter(events_in_last_hour=True)


class Summary(models.Model):
    station = models.ForeignKey('inforecords.Station', models.CASCADE, related_name='summaries')
    date = models.DateField()
    num_events = models.IntegerField(blank=True, null=True)
    num_config = models.IntegerField(blank=True, null=True)
    num_errors = models.IntegerField(blank=True, null=True)
    num_weather = models.IntegerField(blank=True, null=True)
    num_singles = models.IntegerField(blank=True, null=True)
    needs_update = models.BooleanField(default=False)
    needs_update_events = models.BooleanField(default=False)
    needs_update_config = models.BooleanField(default=False)
    needs_update_errors = models.BooleanField(default=False)
    needs_update_weather = models.BooleanField(default=False)
    needs_update_singles = models.BooleanField(default=False)
    events_in_last_hour = models.BooleanField(default=False)

    objects = SummaryQuerySet.as_manager()

    def get_absolute_url(self):
        kwargs = {
            'station_number': self.station.number,
            'date': self.date,
        }
        return reverse('status:station:summary', kwargs=kwargs)

    def __str__(self):
        return f'Summary: {self.station.number} - {self.date}'

    class Meta:
        verbose_name = 'Summary'
        verbose_name_plural = 'Summaries'
        unique_together = ('station', 'date')
        ordering = ['date', 'station']
        get_latest_by = 'date'


class Configuration(models.Model):
    summary = models.ForeignKey(Summary, models.CASCADE, related_name='configurations')
    timestamp = models.DateTimeField()
    gps_latitude = models.FloatField()
    gps_longitude = models.FloatField()
    gps_altitude = models.FloatField()
    mas_version = models.CharField(max_length=40)
    slv_version = models.CharField(max_length=40)
    trig_low_signals = models.PositiveIntegerField()
    trig_high_signals = models.PositiveIntegerField()
    trig_external = models.PositiveIntegerField()
    trig_and_or = models.BooleanField()
    precoinctime = models.FloatField()
    coinctime = models.FloatField()
    postcoinctime = models.FloatField()
    detnum = models.PositiveIntegerField()
    spare_bytes = models.PositiveSmallIntegerField()
    use_filter = models.BooleanField()
    use_filter_threshold = models.BooleanField()
    reduce_data = models.BooleanField()
    startmode = models.BooleanField()
    delay_screen = models.FloatField()
    delay_check = models.FloatField()
    delay_error = models.FloatField()
    mas_ch1_thres_low = models.FloatField()
    mas_ch1_thres_high = models.FloatField()
    mas_ch2_thres_low = models.FloatField()
    mas_ch2_thres_high = models.FloatField()
    mas_ch1_inttime = models.FloatField()
    mas_ch2_inttime = models.FloatField()
    mas_ch1_voltage = models.FloatField()
    mas_ch2_voltage = models.FloatField()
    mas_ch1_current = models.FloatField()
    mas_ch2_current = models.FloatField()
    mas_comp_thres_low = models.FloatField()
    mas_comp_thres_high = models.FloatField()
    mas_max_voltage = models.FloatField()
    mas_reset = models.BooleanField()
    mas_ch1_gain_pos = models.PositiveSmallIntegerField()
    mas_ch1_gain_neg = models.PositiveSmallIntegerField()
    mas_ch2_gain_pos = models.PositiveSmallIntegerField()
    mas_ch2_gain_neg = models.PositiveSmallIntegerField()
    mas_ch1_offset_pos = models.PositiveSmallIntegerField()
    mas_ch1_offset_neg = models.PositiveSmallIntegerField()
    mas_ch2_offset_pos = models.PositiveSmallIntegerField()
    mas_ch2_offset_neg = models.PositiveSmallIntegerField()
    mas_common_offset = models.PositiveSmallIntegerField()
    mas_internal_voltage = models.PositiveSmallIntegerField()
    mas_ch1_adc_gain = models.FloatField()
    mas_ch1_adc_offset = models.FloatField()
    mas_ch2_adc_gain = models.FloatField()
    mas_ch2_adc_offset = models.FloatField()
    mas_ch1_comp_gain = models.FloatField()
    mas_ch1_comp_offset = models.FloatField()
    mas_ch2_comp_gain = models.FloatField()
    mas_ch2_comp_offset = models.FloatField()
    slv_ch1_thres_low = models.FloatField()
    slv_ch1_thres_high = models.FloatField()
    slv_ch2_thres_low = models.FloatField()
    slv_ch2_thres_high = models.FloatField()
    slv_ch1_inttime = models.FloatField()
    slv_ch2_inttime = models.FloatField()
    slv_ch1_voltage = models.FloatField()
    slv_ch2_voltage = models.FloatField()
    slv_ch1_current = models.FloatField()
    slv_ch2_current = models.FloatField()
    slv_comp_thres_low = models.FloatField()
    slv_comp_thres_high = models.FloatField()
    slv_max_voltage = models.FloatField()
    slv_reset = models.BooleanField()
    slv_ch1_gain_pos = models.PositiveSmallIntegerField()
    slv_ch1_gain_neg = models.PositiveSmallIntegerField()
    slv_ch2_gain_pos = models.PositiveSmallIntegerField()
    slv_ch2_gain_neg = models.PositiveSmallIntegerField()
    slv_ch1_offset_pos = models.PositiveSmallIntegerField()
    slv_ch1_offset_neg = models.PositiveSmallIntegerField()
    slv_ch2_offset_pos = models.PositiveSmallIntegerField()
    slv_ch2_offset_neg = models.PositiveSmallIntegerField()
    slv_common_offset = models.PositiveSmallIntegerField()
    slv_internal_voltage = models.PositiveSmallIntegerField()
    slv_ch1_adc_gain = models.FloatField()
    slv_ch1_adc_offset = models.FloatField()
    slv_ch2_adc_gain = models.FloatField()
    slv_ch2_adc_offset = models.FloatField()
    slv_ch1_comp_gain = models.FloatField()
    slv_ch1_comp_offset = models.FloatField()
    slv_ch2_comp_gain = models.FloatField()
    slv_ch2_comp_offset = models.FloatField()

    def __str__(self):
        return f'{self.summary.station.number} - {self.timestamp}'

    class Meta:
        verbose_name = 'Configuration'
        verbose_name_plural = 'Configurations'
        get_latest_by = 'timestamp'
        ordering = ['summary']

    def station(self):
        return self.summary.station.number

    station.admin_order_field = 'summary__station__number'

    @property
    @admin.display(ordering='mas_version')
    def primary(self):
        return self.extract_hardware_serial(self.mas_version)

    @property
    @admin.display(ordering='slv_version')
    def secondary(self):
        return self.extract_hardware_serial(self.slv_version)

    @property
    def primary_fpga(self):
        return self.extract_fpga_version(self.mas_version)

    @property
    def secondary_fpga(self):
        return self.extract_fpga_version(self.slv_version)

    def extract_hardware_serial(self, electronics_version):
        """Extract electronics hardware serial number from version string

        For example from `Hardware: 32 FPGA: 15' the integer 32 is extracted.
        If the number is not found or 0 the returned value is -1.

        :param electronics_version: version string from the configuration.
        :return: extracted hardware serial as integer, -1 is not found.

        """
        result = re.search(r'\d+', electronics_version)
        if result is None:
            serial = -1
        else:
            serial = int(result.group())
            if serial == 0:
                serial = -1
        return serial

    def extract_fpga_version(self, electronics_version):
        """Extract electronics hardware serial number from version string

        For example from `Hardware: 32 FPGA: 15' the integer 15 is extracted.
        If the number is not found or 0 the returned value is -1.

        :param electronics_version: version string from the configuration.
        :return: extracted FPGA version as integer, -1 is not found.

        """
        try:
            version = int(re.findall(r'\d+', electronics_version)[1])
        except IndexError:
            version = -1
        else:
            if version == 0:
                version = -1
        return version


class HistogramType(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=20, unique=True)
    has_multiple_datasets = models.BooleanField(default=False)
    bin_axis_title = models.CharField(max_length=40)
    value_axis_title = models.CharField(max_length=40)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Histogram type'
        verbose_name_plural = 'Histogram types'


class DatasetType(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=20, unique=True)
    has_multiple_datasets = models.BooleanField(default=False)
    x_axis_title = models.CharField(max_length=40)
    y_axis_title = models.CharField(max_length=40)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Dataset type'
        verbose_name_plural = 'Dataset types'


class NetworkHistogram(models.Model):
    network_summary = models.ForeignKey(NetworkSummary, models.CASCADE, related_name='network_histograms')
    type = models.ForeignKey(HistogramType, models.CASCADE, related_name='network_histograms')
    bins = ArrayField(models.PositiveIntegerField())
    values = ArrayField(models.PositiveIntegerField())

    def get_absolute_url(self):
        kwargs = {'date': self.network_summary.date}
        return reverse(f'status:source:{self.type.slug}', kwargs=kwargs)

    def __str__(self):
        return f'{self.network_summary.date} - {self.type}'

    class Meta:
        verbose_name = 'Network histogram'
        verbose_name_plural = 'Network histograms'
        unique_together = ('network_summary', 'type')
        ordering = ['network_summary', 'type']


class BaseDailyStationDataMixin(models.Model):
    """Base class for daily station data models"""

    def get_absolute_url(self):
        kwargs = {
            'station_number': self.summary.station.number,
            'date': self.summary.date,
        }
        return reverse(f'status:source:{self.type.slug}', kwargs=kwargs)

    def __str__(self):
        return f'{self.summary.station.number} - {self.summary.date} - {self.type}'

    class Meta:
        abstract = True
        unique_together = ('summary', 'type')
        ordering = ['summary', 'type']


class DailyHistogram(BaseDailyStationDataMixin):
    summary = models.ForeignKey(Summary, models.CASCADE, related_name='histograms')
    type = models.ForeignKey(HistogramType, models.CASCADE, related_name='histograms')
    bins = ArrayField(models.PositiveIntegerField())
    values = ArrayField(models.PositiveIntegerField())


class MultiDailyHistogram(BaseDailyStationDataMixin):
    summary = models.ForeignKey(Summary, models.CASCADE, related_name='multi_histograms')
    type = models.ForeignKey(HistogramType, models.CASCADE, related_name='multi_histograms')
    bins = ArrayField(models.PositiveIntegerField())
    values = ArrayField(ArrayField(models.PositiveIntegerField()), size=4)


class DailyDataset(BaseDailyStationDataMixin):
    summary = models.ForeignKey(Summary, models.CASCADE, related_name='datasets')
    type = models.ForeignKey(DatasetType, models.CASCADE, related_name='datasets')
    x = ArrayField(models.PositiveIntegerField())
    y = ArrayField(models.FloatField())


class MultiDailyDataset(BaseDailyStationDataMixin):
    summary = models.ForeignKey(Summary, models.CASCADE, related_name='multi_datasets')
    type = models.ForeignKey(DatasetType, models.CASCADE, related_name='multi_datasets')
    x = ArrayField(models.PositiveIntegerField())
    y = ArrayField(ArrayField(models.FloatField()), size=4)


class GeneratorState(models.Model):
    check_last_run = models.DateTimeField()
    check_is_running = models.BooleanField(default=False)
    update_last_run = models.DateTimeField()
    update_is_running = models.BooleanField(default=False)

    def update_has_finished(self, day=None):
        """Determine if the daily update at date has finished successfully

        :param day: datetime.date

        """
        if day is None:
            day = datetime.date.today()

        if self.update_last_run.date() >= day and not self.update_is_running:
            return True
        else:
            return False


class DetectorTimingOffset(models.Model):
    summary = models.ForeignKey(Summary, models.CASCADE, related_name='detector_timing_offsets')
    offset_1 = models.FloatField(blank=True, null=True)
    offset_2 = models.FloatField(blank=True, null=True)
    offset_3 = models.FloatField(blank=True, null=True)
    offset_4 = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = 'Detector timing offset'
        verbose_name_plural = 'Detector timing offsets'
        ordering = ['summary']


class StationTimingOffset(models.Model):
    ref_summary = models.ForeignKey(Summary, models.CASCADE, related_name='ref_station_offsets')
    summary = models.ForeignKey(Summary, models.CASCADE, related_name='station_offsets')
    offset = models.FloatField(blank=True, null=True)
    error = models.FloatField(blank=True, null=True)

    def clean(self):
        if self.ref_summary.station == self.summary.station:
            raise ValidationError("The stations may not be the same")
        if self.ref_summary.date != self.summary.date:
            raise ValidationError("The summary dates should be the same")

    class Meta:
        verbose_name = 'Station timing offset'
        verbose_name_plural = 'Station timing offsets'
        unique_together = ('ref_summary', 'summary')
        ordering = ['ref_summary']
