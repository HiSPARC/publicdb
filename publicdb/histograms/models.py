import datetime
import re

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

FIRSTDATE = datetime.date(2004, 1, 1)


class NetworkSummaryQuerySet(models.QuerySet):
    def valid_date(self):
        """Filter by date to dates between start and today"""
        return self.filter(
            date__gte=FIRSTDATE,
            date__lte=datetime.date.today())

    def with_coincidences(self):
        return self.valid_date().filter(
            num_coincidences__isnull=False)


class NetworkSummary(models.Model):
    date = models.DateField(unique=True)
    num_coincidences = models.IntegerField(blank=True, null=True)
    needs_update = models.BooleanField(default=False)
    needs_update_coincidences = models.BooleanField(default=False)

    objects = NetworkSummaryQuerySet.as_manager()

    def get_absolute_url(self):
        kwargs = {'year': self.date.year,
                  'month': self.date.month,
                  'day': self.date.day}
        return reverse('status:network:coincidences', kwargs=kwargs)

    def __unicode__(self):
        return 'Network Summary: %s' % (self.date.strftime('%d %b %Y'))

    class Meta:
        verbose_name = 'Network summary'
        verbose_name_plural = 'Network summaries'
        ordering = ['date']
        get_latest_by = 'date'


class SummaryQuerySet(models.QuerySet):
    def valid_date(self):
        """Filter by date to dates between start and today"""
        return self.filter(
            date__gte=FIRSTDATE,
            date__lte=datetime.date.today())

    def with_data(self):
        """Filter with at least either events or weather data"""
        return self.valid_date().filter(
            models.Q(num_events__isnull=False) |
            models.Q(num_weather__isnull=False))

    def with_config(self):
        """Filter with at least configurations"""
        return self.valid_date().filter(
            num_config__isnull=False)


class Summary(models.Model):
    station = models.ForeignKey('inforecords.Station', models.CASCADE)
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

    objects = SummaryQuerySet.as_manager()

    def get_absolute_url(self):
        kwargs = {'station_number': self.station.number,
                  'year': self.date.year,
                  'month': self.date.month,
                  'day': self.date.day}
        return reverse('status:station:data', kwargs=kwargs)

    def __unicode__(self):
        return 'Summary: %d - %s' % (self.station.number,
                                     self.date.strftime('%d %b %Y'))

    class Meta:
        verbose_name = 'Summary'
        verbose_name_plural = 'Summaries'
        unique_together = ('station', 'date')
        ordering = ['date', 'station']
        get_latest_by = 'date'


class Configuration(models.Model):
    source = models.ForeignKey(Summary, models.CASCADE)
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

    def __unicode__(self):
        return "%d - %s" % (self.source.station.number, self.timestamp)

    class Meta:
        verbose_name = 'Configuration'
        verbose_name_plural = 'Configurations'
        get_latest_by = 'timestamp'
        ordering = ['source']

    def station(self):
        return self.source.station.number
    station.admin_order_field = 'source__station__number'

    def _master(self):
        return self.extract_hardware_serial(self.mas_version)
    _master.admin_order_field = 'mas_version'

    master = property(_master)

    def _slave(self):
        return self.extract_hardware_serial(self.slv_version)
    _slave.admin_order_field = 'slv_version'

    slave = property(_slave)

    @property
    def master_fpga(self):
        return self.extract_fpga_version(self.mas_version)

    @property
    def slave_fpga(self):
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

    def __unicode__(self):
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

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Dataset type'
        verbose_name_plural = 'Dataset types'


class NetworkHistogram(models.Model):
    source = models.ForeignKey(NetworkSummary, models.CASCADE)
    type = models.ForeignKey(HistogramType, models.CASCADE)
    bins = ArrayField(models.PositiveIntegerField())
    values = ArrayField(models.PositiveIntegerField())

    def get_absolute_url(self):
        kwargs = {'year': self.source.date.year,
                  'month': self.source.date.month,
                  'day': self.source.date.day}
        return reverse('status:source:{type}'.format(type=self.type.slug), kwargs=kwargs)

    def __unicode__(self):
        return '%s - %s' % (self.source.date.strftime('%d %b %Y'), self.type)

    class Meta:
        verbose_name = 'Network histogram'
        verbose_name_plural = 'Network histograms'
        unique_together = ('source', 'type')
        ordering = ['source', 'type']


class BaseDailyStationDataMixin(models.Model):
    """Base class for daily station data models"""

    def get_absolute_url(self):
        kwargs = {'station_number': self.source.station.number,
                  'year': self.source.date.year,
                  'month': self.source.date.month,
                  'day': self.source.date.day}
        return reverse('status:source:{type}'.format(type=self.type.slug), kwargs=kwargs)

    def __unicode__(self):
        return "%d - %s - %s" % (self.source.station.number,
                                 self.source.date.strftime('%d %b %Y'),
                                 self.type)

    class Meta:
        abstract = True
        unique_together = ('source', 'type')
        ordering = ['source', 'type']


class DailyHistogram(BaseDailyStationDataMixin):
    source = models.ForeignKey(Summary, models.CASCADE)
    type = models.ForeignKey(HistogramType, models.CASCADE)
    bins = ArrayField(models.PositiveIntegerField())
    values = ArrayField(models.PositiveIntegerField())


class MultiDailyHistogram(BaseDailyStationDataMixin):
    source = models.ForeignKey(Summary, models.CASCADE)
    type = models.ForeignKey(HistogramType, models.CASCADE)
    bins = ArrayField(models.PositiveIntegerField())
    values = ArrayField(ArrayField(models.PositiveIntegerField()), size=4)


class DailyDataset(BaseDailyStationDataMixin):
    source = models.ForeignKey(Summary, models.CASCADE)
    type = models.ForeignKey(DatasetType, models.CASCADE)
    x = ArrayField(models.PositiveIntegerField())
    y = ArrayField(models.FloatField())


class MultiDailyDataset(BaseDailyStationDataMixin):
    source = models.ForeignKey(Summary, models.CASCADE)
    type = models.ForeignKey(DatasetType, models.CASCADE)
    x = ArrayField(models.PositiveIntegerField())
    y = ArrayField(ArrayField(models.FloatField()), size=4)


class GeneratorState(models.Model):
    check_last_run = models.DateTimeField()
    check_is_running = models.BooleanField(default=False)
    update_last_run = models.DateTimeField()
    update_is_running = models.BooleanField(default=False)


class PulseheightFit(models.Model):
    DETECTOR_CHOICES = ((1, 'Scintillator 1'),
                        (2, 'Scintillator 2'),
                        (3, 'Scintillator 3'),
                        (4, 'Scintillator 4'))

    source = models.ForeignKey(Summary, models.CASCADE)
    plate = models.IntegerField(choices=DETECTOR_CHOICES)

    initial_mpv = models.FloatField()
    initial_width = models.FloatField()

    fitted_mpv = models.FloatField()
    fitted_mpv_error = models.FloatField()
    fitted_width = models.FloatField()
    fitted_width_error = models.FloatField()

    degrees_of_freedom = models.IntegerField(default=0)
    chi_square_reduced = models.FloatField()

    error_type = models.CharField(default="", max_length=64)
    error_message = models.TextField(default="")

    def station(self):
        return self.source.station.number
    station.admin_order_field = 'source__station__number'

    def date(self):
        return self.source.date
    date.admin_order_field = 'source__date'

    def __unicode__(self):
        return "%d - %s - %d" % (self.source.station.number,
                                 self.source.date.strftime('%d %b %Y'),
                                 self.plate)

    class Meta:
        verbose_name = 'Pulseheight fit'
        verbose_name_plural = 'Pulseheight fits'
        unique_together = ('source', 'plate')
        ordering = ['source', 'plate']


class DetectorTimingOffset(models.Model):
    source = models.ForeignKey(Summary, models.CASCADE)
    offset_1 = models.FloatField(blank=True, null=True)
    offset_2 = models.FloatField(blank=True, null=True)
    offset_3 = models.FloatField(blank=True, null=True)
    offset_4 = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = 'Detector timing offset'
        verbose_name_plural = 'Detector timing offsets'
        ordering = ['source']


class StationTimingOffset(models.Model):
    ref_source = models.ForeignKey(Summary, models.CASCADE, related_name='ref_station_offsets')
    source = models.ForeignKey(Summary, models.CASCADE, related_name='station_offsets')
    offset = models.FloatField(blank=True, null=True)
    error = models.FloatField(blank=True, null=True)

    def clean(self):
        if self.ref_source.station == self.source.station:
            raise ValidationError("The stations may not be the same")
        if self.ref_source.date != self.source.date:
            raise ValidationError("The summary dates should be the same")

    class Meta:
        verbose_name = 'Station timing offset'
        verbose_name_plural = 'Station timing offsets'
        unique_together = ('ref_source', 'source')
        ordering = ['ref_source']
