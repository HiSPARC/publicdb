from datetime import date

import factory

from publicdb.histograms import models

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
    source = factory.SubFactory(SummaryFactory)
    timestamp = factory.Faker('past_datetime', start_date=date(2004, 1, 1))
    gps_latitude = factory.Faker('latitude')
    gps_longitude = factory.Faker('longitude')
    gps_altitude = factory.Faker('pyfloat')
    mas_version = factory.Faker('word')
    slv_version = factory.Faker('word')
    trig_low_signals = factory.Faker('random_int', min=0, max=1)
    trig_high_signals = factory.Faker('random_int', min=0, max=1)
    trig_external = factory.Faker('random_int', min=0, max=1)
    trig_and_or = factory.Faker('boolean')
    precoinctime = factory.Faker('pyfloat', left_digits=1, right_digits=1, positive=True)
    coinctime = factory.Faker('pyfloat', left_digits=1, right_digits=1, positive=True)
    postcoinctime = factory.Faker('pyfloat', left_digits=1, right_digits=1, positive=True)
    detnum = factory.Faker('random_int', min=0, max=99999)
    spare_bytes = factory.Faker('random_int', min=0, max=1)
    use_filter = factory.Faker('boolean')
    use_filter_threshold = factory.Faker('boolean')
    reduce_data = factory.Faker('boolean')
    startmode = factory.Faker('boolean')
    delay_screen = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    delay_check = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    delay_error = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    mas_ch1_thres_low = factory.Faker('pyfloat', left_digits=3, right_digits=0, positive=True)
    mas_ch1_thres_high = factory.Faker('pyfloat', left_digits=3, right_digits=0, positive=True)
    mas_ch2_thres_low = factory.Faker('pyfloat', left_digits=3, right_digits=0, positive=True)
    mas_ch2_thres_high = factory.Faker('pyfloat', left_digits=3, right_digits=0, positive=True)
    mas_ch1_inttime = factory.Faker('pyfloat', positive=True)
    mas_ch2_inttime = factory.Faker('pyfloat', positive=True)
    mas_ch1_voltage = factory.Faker('pyfloat', positive=True)
    mas_ch2_voltage = factory.Faker('pyfloat', positive=True)
    mas_ch1_current = factory.Faker('pyfloat', positive=True)
    mas_ch2_current = factory.Faker('pyfloat', positive=True)
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
    slv_ch1_thres_low = factory.Faker('pyfloat')
    slv_ch1_thres_high = factory.Faker('pyfloat')
    slv_ch2_thres_low = factory.Faker('pyfloat')
    slv_ch2_thres_high = factory.Faker('pyfloat')
    slv_ch1_inttime = factory.Faker('pyfloat')
    slv_ch2_inttime = factory.Faker('pyfloat')
    slv_ch1_voltage = factory.Faker('pyfloat')
    slv_ch2_voltage = factory.Faker('pyfloat')
    slv_ch1_current = factory.Faker('pyfloat')
    slv_ch2_current = factory.Faker('pyfloat')
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
    source = factory.SubFactory(NetworkSummaryFactory)
    type = factory.SubFactory(HistogramTypeFactory)
    bins = factory.LazyAttribute(lambda o: range(len(o.values)))
    values = factory.Faker('int_list')

    class Meta:
        model = models.NetworkHistogram


class DailyHistogramFactory(factory.DjangoModelFactory):
    source = factory.SubFactory(SummaryFactory)
    type = factory.SubFactory(HistogramTypeFactory)
    bins = factory.LazyAttribute(lambda o: range(len(o.values)))
    values = factory.Faker('float_list')

    class Meta:
        model = models.DailyHistogram


class DailyDatasetFactory(factory.DjangoModelFactory):
    source = factory.SubFactory(SummaryFactory)
    type = factory.SubFactory(DatasetTypeFactory)
    x = factory.Faker('int_list')
    y = factory.Faker('int_list')

    class Meta:
        model = models.DailyDataset
