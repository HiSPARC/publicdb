import ast
import base64
import cPickle as pickle
import re
import zlib

from django.core.exceptions import ValidationError
from django.db import models


class SerializedDataField(models.Field):

    def db_type(self, connection):
        return 'BYTEA'

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        try:
            unpickled = pickle.loads(zlib.decompress(base64.b64decode(value)))
        except Exception:
            return value
        else:
            return unpickled

    def get_prep_value(self, value):
        return base64.b64encode(zlib.compress(pickle.dumps(value)))


class NetworkSummary(models.Model):
    date = models.DateField(unique=True)
    num_coincidences = models.IntegerField(blank=True, null=True)
    needs_update = models.BooleanField(default=False)
    needs_update_coincidences = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Network Summary: %s' % (self.date.strftime('%d %b %Y'))

    class Meta:
        verbose_name_plural = 'network summaries'
        ordering = ('date',)
        get_latest_by = 'date'


class Summary(models.Model):
    station = models.ForeignKey('inforecords.Station')
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

    def __unicode__(self):
        return 'Summary: %d - %s' % (self.station.number,
                                     self.date.strftime('%d %b %Y'))

    class Meta:
        verbose_name_plural = 'summaries'
        unique_together = ('station', 'date')
        ordering = ('date', 'station')
        get_latest_by = 'date'


class Configuration(models.Model):
    source = models.ForeignKey('Summary')
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
        verbose_name_plural = 'configurations'
        get_latest_by = 'timestamp'
        ordering = ('source',)

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


class NetworkHistogram(models.Model):
    source = models.ForeignKey('NetworkSummary')
    type = models.ForeignKey('HistogramType')
    bins = SerializedDataField()
    values = SerializedDataField()

    def save(self, *args, **kwargs):
        """Ensure the stored bins and values are numbers

        Saving a model via the admin interface can cause the list to be
        interpreted as unicode. This code converts the strings to
        numbers in a safe way.

        """
        if isinstance(self.bins, basestring):
            self.bins = ast.literal_eval(self.bins)
        if isinstance(self.values, basestring):
            self.values = ast.literal_eval(self.values)
        super(NetworkHistogram, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s - %s' % (self.source.date.strftime('%d %b %Y'), self.type)

    class Meta:
        unique_together = ('source', 'type')
        ordering = ('source', 'type')


class DailyHistogram(models.Model):
    source = models.ForeignKey('Summary')
    type = models.ForeignKey('HistogramType')
    bins = SerializedDataField()
    values = SerializedDataField()

    def save(self, *args, **kwargs):
        """Ensure the stored bins and values are numbers

        Saving a model via the admin interface can cause the list to be
        interpreted as unicode. This code converts the strings to
        numbers in a safe way.

        """
        if isinstance(self.bins, basestring):
            self.bins = ast.literal_eval(self.bins)
        if isinstance(self.values, basestring):
            self.values = ast.literal_eval(self.values)
        super(DailyHistogram, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%d - %s - %s" % (self.source.station.number,
                                 self.source.date.strftime('%d %b %Y'),
                                 self.type)

    class Meta:
        unique_together = ('source', 'type')
        ordering = ('source', 'type')


class DailyDataset(models.Model):
    source = models.ForeignKey('Summary')
    type = models.ForeignKey('DatasetType')
    x = SerializedDataField()
    y = SerializedDataField()

    def save(self, *args, **kwargs):
        """Ensure the stored values are numbers

        Saving a model via the admin interface can cause the list to be
        interpreted as unicode. This code converts the strings to
        numbers in a safe way.

        """
        if isinstance(self.x, basestring):
            self.x = ast.literal_eval(self.x)
        if isinstance(self.y, basestring):
            self.y = ast.literal_eval(self.y)
        super(DailyDataset, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%d - %s - %s" % (self.source.station.number,
                                 self.source.date.strftime('%d %b %Y'),
                                 self.type)

    class Meta:
        unique_together = ('source', 'type')
        ordering = ('source', 'type')


class HistogramType(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=20, unique=True)
    has_multiple_datasets = models.BooleanField(default=False)
    bin_axis_title = models.CharField(max_length=40)
    value_axis_title = models.CharField(max_length=40)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class DatasetType(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=20, unique=True)
    x_axis_title = models.CharField(max_length=40)
    y_axis_title = models.CharField(max_length=40)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


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

    source = models.ForeignKey('Summary')
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
        verbose_name_plural = 'Pulseheight fit'
        unique_together = ('source', 'plate')
        ordering = ('source', 'plate')


class DetectorTimingOffset(models.Model):
    source = models.ForeignKey('Summary')
    offset_1 = models.FloatField(blank=True, null=True)
    offset_2 = models.FloatField(blank=True, null=True)
    offset_3 = models.FloatField(blank=True, null=True)
    offset_4 = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ('source',)


class StationTimingOffset(models.Model):
    ref_source = models.ForeignKey('Summary', related_name='ref_source')
    source = models.ForeignKey('Summary', related_name='source')
    offset = models.FloatField(blank=True, null=True)
    error = models.FloatField(blank=True, null=True)

    def clean(self):
        if self.ref_source.station == self.source.station:
            raise ValidationError("The stations may not be the same")
        if self.ref_source.date != self.source.date:
            raise ValidationError("The summary dates should be the same")

    class Meta:
        unique_together = ('ref_source', 'source')
        ordering = ('ref_source',)
