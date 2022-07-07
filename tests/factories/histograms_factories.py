from datetime import date

import factory
import numpy

from publicdb.histograms import jobs, models

from . import inforecords_factories
from .providers import DataProvider

factory.Faker.add_provider(DataProvider)


class NetworkSummaryFactory(factory.DjangoModelFactory):
    date = factory.Faker('past_date', start_date=date(2004, 1, 1))
    num_coincidences = factory.Faker('random_int', min=0, max=30000)
    needs_update = factory.Faker('boolean')
    needs_update_coincidences = factory.Faker('boolean')

    class Meta:
        model = models.NetworkSummary
        django_get_or_create = ('date',)


class SummaryFactory(factory.DjangoModelFactory):
    station = factory.SubFactory(inforecords_factories.StationFactory)
    date = factory.Faker('past_date', start_date=date(2004, 1, 1))
    num_events = factory.Faker('random_int', min=0, max=3000)
    num_config = factory.Faker('random_int', min=0, max=5)
    num_errors = factory.Faker('random_int', min=0, max=5)
    num_weather = factory.Faker('random_int', min=0, max=3000)
    num_singles = factory.Faker('random_int', min=0, max=86400)
    needs_update = factory.Faker('boolean')
    needs_update_events = factory.Faker('boolean')
    needs_update_config = factory.Faker('boolean')
    needs_update_errors = factory.Faker('boolean')
    needs_update_weather = factory.Faker('boolean')
    needs_update_singles = factory.Faker('boolean')

    class Meta:
        model = models.Summary
        django_get_or_create = ('station', 'date')


class ConfigurationFactory(factory.DjangoModelFactory):
    summary = factory.SubFactory(SummaryFactory)
    timestamp = factory.Faker('past_datetime', start_date=date(2004, 1, 1))
    gps_latitude = factory.Faker('latitude')
    gps_longitude = factory.Faker('longitude')
    gps_altitude = factory.Faker('float', min=-100, max=100)
    mas_version = factory.Faker('numerify', text='Hardware: @% FPGA: @%')
    slv_version = factory.Faker('numerify', text='Hardware: @% FPGA: @%')
    trig_low_signals = factory.Faker('random_int', min=0, max=1)
    trig_high_signals = factory.Faker('random_int', min=0, max=1)
    trig_external = factory.Faker('random_int', min=0, max=1)
    trig_and_or = factory.Faker('boolean')
    precoinctime = factory.Faker('float', min=0, max=2)
    coinctime = factory.Faker('float', min=0, max=5)
    postcoinctime = factory.Faker('float', min=0, max=8)
    detnum = factory.Faker('random_int', min=0, max=99999)
    spare_bytes = factory.Faker('random_int', min=0, max=1)
    use_filter = factory.Faker('boolean')
    use_filter_threshold = factory.Faker('boolean')
    reduce_data = factory.Faker('boolean')
    startmode = factory.Faker('boolean')
    delay_screen = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    delay_check = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    delay_error = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    mas_ch1_thres_low = factory.Faker('float', min=-500, max=0)
    mas_ch1_thres_high = factory.Faker('float', min=-500, max=0)
    mas_ch2_thres_low = factory.Faker('float', min=-500, max=0)
    mas_ch2_thres_high = factory.Faker('float', min=-500, max=0)
    mas_ch1_inttime = factory.Faker('float', min=0, max=100)
    mas_ch2_inttime = factory.Faker('float', min=0, max=100)
    mas_ch1_voltage = factory.Faker('float', min=0, max=1500)
    mas_ch2_voltage = factory.Faker('float', min=0, max=1500)
    mas_ch1_current = factory.Faker('float', min=0, max=15)
    mas_ch2_current = factory.Faker('float', min=0, max=15)
    mas_comp_thres_low = factory.Faker('pyfloat')
    mas_comp_thres_high = factory.Faker('pyfloat')
    mas_max_voltage = factory.Faker('pyfloat')
    mas_reset = factory.Faker('boolean')
    mas_ch1_gain_pos = factory.Faker('random_int', min=0, max=255)
    mas_ch1_gain_neg = factory.Faker('random_int', min=0, max=255)
    mas_ch2_gain_pos = factory.Faker('random_int', min=0, max=255)
    mas_ch2_gain_neg = factory.Faker('random_int', min=0, max=255)
    mas_ch1_offset_pos = factory.Faker('random_int', min=0, max=255)
    mas_ch1_offset_neg = factory.Faker('random_int', min=0, max=255)
    mas_ch2_offset_pos = factory.Faker('random_int', min=0, max=255)
    mas_ch2_offset_neg = factory.Faker('random_int', min=0, max=255)
    mas_common_offset = factory.Faker('random_int', min=0, max=255)
    mas_internal_voltage = factory.Faker('random_int', min=0, max=255)
    mas_ch1_adc_gain = factory.Faker('pyfloat')
    mas_ch1_adc_offset = factory.Faker('pyfloat')
    mas_ch2_adc_gain = factory.Faker('pyfloat')
    mas_ch2_adc_offset = factory.Faker('pyfloat')
    mas_ch1_comp_gain = factory.Faker('pyfloat')
    mas_ch1_comp_offset = factory.Faker('pyfloat')
    mas_ch2_comp_gain = factory.Faker('pyfloat')
    mas_ch2_comp_offset = factory.Faker('pyfloat')
    slv_ch1_thres_low = factory.Faker('float', min=-500, max=0)
    slv_ch1_thres_high = factory.Faker('float', min=-500, max=0)
    slv_ch2_thres_low = factory.Faker('float', min=-500, max=0)
    slv_ch2_thres_high = factory.Faker('float', min=-500, max=0)
    slv_ch1_inttime = factory.Faker('float', min=0, max=100)
    slv_ch2_inttime = factory.Faker('float', min=0, max=100)
    slv_ch1_voltage = factory.Faker('float', min=0, max=1500)
    slv_ch2_voltage = factory.Faker('float', min=0, max=1500)
    slv_ch1_current = factory.Faker('float', min=0, max=15)
    slv_ch2_current = factory.Faker('float', min=0, max=15)
    slv_comp_thres_low = factory.Faker('pyfloat')
    slv_comp_thres_high = factory.Faker('pyfloat')
    slv_max_voltage = factory.Faker('pyfloat')
    slv_reset = factory.Faker('boolean')
    slv_ch1_gain_pos = factory.Faker('random_int', min=0, max=255)
    slv_ch1_gain_neg = factory.Faker('random_int', min=0, max=255)
    slv_ch2_gain_pos = factory.Faker('random_int', min=0, max=255)
    slv_ch2_gain_neg = factory.Faker('random_int', min=0, max=255)
    slv_ch1_offset_pos = factory.Faker('random_int', min=0, max=255)
    slv_ch1_offset_neg = factory.Faker('random_int', min=0, max=255)
    slv_ch2_offset_pos = factory.Faker('random_int', min=0, max=255)
    slv_ch2_offset_neg = factory.Faker('random_int', min=0, max=255)
    slv_common_offset = factory.Faker('random_int', min=0, max=255)
    slv_internal_voltage = factory.Faker('random_int', min=0, max=255)
    slv_ch1_adc_gain = factory.Faker('pyfloat')
    slv_ch1_adc_offset = factory.Faker('pyfloat')
    slv_ch2_adc_gain = factory.Faker('pyfloat')
    slv_ch2_adc_offset = factory.Faker('pyfloat')
    slv_ch1_comp_gain = factory.Faker('pyfloat')
    slv_ch1_comp_offset = factory.Faker('pyfloat')
    slv_ch2_comp_gain = factory.Faker('pyfloat')
    slv_ch2_comp_offset = factory.Faker('pyfloat')

    class Meta:
        model = models.Configuration


class HistogramTypeFactory(factory.DjangoModelFactory):
    name = factory.Faker('word')
    slug = factory.Faker('slug')
    has_multiple_datasets = factory.Faker('boolean')
    bin_axis_title = factory.Faker('word')
    value_axis_title = factory.Faker('word')
    description = factory.Faker('sentence')

    class Meta:
        model = models.HistogramType
        django_get_or_create = ('slug',)


class DatasetTypeFactory(factory.DjangoModelFactory):
    name = factory.Faker('word')
    slug = factory.Faker('slug')
    x_axis_title = factory.Faker('word')
    y_axis_title = factory.Faker('word')
    description = factory.Faker('sentence')

    class Meta:
        model = models.DatasetType
        django_get_or_create = ('slug',)


class NetworkHistogramFactory(factory.DjangoModelFactory):
    network_summary = factory.SubFactory(NetworkSummaryFactory)
    type = factory.SubFactory(HistogramTypeFactory)
    bins = factory.LazyAttribute(lambda o: list(range(len(o.values) + 1)))
    values = factory.Faker('int_list')

    class Meta:
        model = models.NetworkHistogram


class CoincidencetimeHistogramFactory(NetworkHistogramFactory):
    type = factory.SubFactory(HistogramTypeFactory, slug='coincidencetime')
    bins = numpy.linspace(0, 24, 24 + 1).tolist()
    values = factory.Faker('int_list', n=24, min=0, max=10000)


class CoincidencenumberHistogramFactory(NetworkHistogramFactory):
    type = factory.SubFactory(HistogramTypeFactory, slug='coincidencenumber')
    bins = numpy.linspace(0, 100, 100 + 1).tolist()
    values = factory.Faker('int_list', n=100, min=0, max=10000)


class DailyHistogramFactory(factory.DjangoModelFactory):
    summary = factory.SubFactory(SummaryFactory)
    type = factory.SubFactory(HistogramTypeFactory)
    bins = factory.LazyAttribute(lambda o: list(range(len(o.values) + 1)))
    values = factory.Faker('int_list')

    class Meta:
        model = models.DailyHistogram


class EventtimeHistogramFactory(DailyHistogramFactory):
    type = factory.SubFactory(HistogramTypeFactory, slug='eventtime')
    bins = numpy.linspace(0, 24, 24 + 1).tolist()
    values = factory.Faker('int_list', n=24, min=0, max=10000)


class AzimuthHistogramFactory(DailyHistogramFactory):
    type = factory.SubFactory(HistogramTypeFactory, slug='azimuth')
    bins = numpy.linspace(-180, 180, 30 + 1).tolist()
    values = factory.Faker('int_list', n=30, min=0, max=600)


class ZenithHistogramFactory(DailyHistogramFactory):
    type = factory.SubFactory(HistogramTypeFactory, slug='zenith')
    bins = numpy.linspace(0, 90, 30 + 1).tolist()
    values = factory.Faker('int_list', n=jobs.BIN_PH_NUM, min=0, max=1000)


class MultiDailyHistogramFactory(DailyHistogramFactory):
    values = factory.Faker('multi_int_list')

    class Meta:
        model = models.MultiDailyHistogram


class PulseintegralHistogramFactory(MultiDailyHistogramFactory):
    type = factory.SubFactory(HistogramTypeFactory, slug='pulseintegral')
    bins = numpy.linspace(0, jobs.MAX_IN, jobs.BIN_IN_NUM + 1).tolist()
    values = factory.Faker('multi_int_list', n=jobs.BIN_IN_NUM, min=0, max=10000)


class PulseheightHistogramFactory(MultiDailyHistogramFactory):
    type = factory.SubFactory(HistogramTypeFactory, slug='pulseheight')
    bins = numpy.linspace(0, jobs.MAX_PH, jobs.BIN_PH_NUM + 1).tolist()
    values = factory.Faker('multi_int_list', n=jobs.BIN_PH_NUM, min=0, max=10000)


class SingleslowHistogramFactory(MultiDailyHistogramFactory):
    type = factory.SubFactory(HistogramTypeFactory, slug='singleslow')
    bins = numpy.linspace(0, jobs.MAX_SINGLES_LOW, jobs.BIN_SINGLES_LOW_NUM + 1).tolist()
    values = factory.Faker('multi_int_list', n=jobs.BIN_SINGLES_LOW_NUM, min=0, max=40000)


class SingleshighHistogramFactory(MultiDailyHistogramFactory):
    type = factory.SubFactory(HistogramTypeFactory, slug='singleshigh')
    bins = numpy.linspace(0, jobs.MAX_SINGLES_HIGH, jobs.BIN_SINGLES_HIGH_NUM + 1).tolist()
    values = factory.Faker('multi_int_list', n=jobs.BIN_SINGLES_HIGH_NUM, min=0, max=20000)


class DailyDatasetFactory(factory.DjangoModelFactory):
    summary = factory.SubFactory(SummaryFactory)
    type = factory.SubFactory(DatasetTypeFactory)
    x = factory.Faker('int_list')
    y = factory.Faker('float_list')

    class Meta:
        model = models.DailyDataset


class TemperatureDatasetFactory(DailyDatasetFactory):
    type = factory.SubFactory(DatasetTypeFactory, slug='temperature')
    x = numpy.arange(0, 86401, jobs.INTERVAL_TEMP).tolist()
    y = factory.Faker('float_list', n=(86400 // jobs.INTERVAL_TEMP), min=-20, max=40)


class BarometerDatasetFactory(DailyDatasetFactory):
    type = factory.SubFactory(DatasetTypeFactory, slug='barometer')
    x = numpy.arange(0, 86401, jobs.INTERVAL_BARO).tolist()
    y = factory.Faker('float_list', n=(86400 // jobs.INTERVAL_BARO), min=900, max=1200)


class MultiDailyDatasetFactory(DailyDatasetFactory):
    y = factory.Faker('multi_float_list')

    class Meta:
        model = models.MultiDailyDataset


class SinglesratelowDatasetFactory(MultiDailyDatasetFactory):
    type = factory.SubFactory(DatasetTypeFactory, slug='singlesratelow')
    x = numpy.arange(0, 86401, jobs.BIN_SINGLES_RATE).tolist()
    y = factory.Faker('multi_float_list', n=(86400 // jobs.BIN_SINGLES_RATE), min=0, max=400)


class SinglesratehighDatasetFactory(MultiDailyDatasetFactory):
    type = factory.SubFactory(DatasetTypeFactory, slug='singlesratehigh')
    x = numpy.arange(0, 86401, jobs.BIN_SINGLES_RATE).tolist()
    y = factory.Faker('multi_float_list', n=(86400 // jobs.BIN_SINGLES_RATE), min=0, max=200)


class DetectorTimingOffsetFactory(factory.DjangoModelFactory):
    summary = factory.SubFactory(SummaryFactory)
    offset_1 = factory.Faker('float', min=-100, max=100)
    offset_2 = factory.Faker('float', min=-100, max=100)
    offset_3 = factory.Faker('float', min=-100, max=100)
    offset_4 = factory.Faker('float', min=-100, max=100)

    class Meta:
        model = models.DetectorTimingOffset


class StationTimingOffsetFactory(factory.DjangoModelFactory):
    ref_summary = factory.SubFactory(SummaryFactory)
    summary = factory.SubFactory(SummaryFactory)
    offset = factory.Faker('float', min=-1000, max=1000)
    error = factory.Faker('float', min=0, max=100)

    class Meta:
        model = models.StationTimingOffset
