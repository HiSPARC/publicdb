import factory

from publicdb.histograms import models

from . import inforecord_factories
from .providers import DataProvider

factory.Faker.add_provider(DataProvider)


class NetworkSummaryFactory(factory.DjangoModelFactory):
    date = factory.Faker('past_date', start_date='2004-01-01')
    num_coincidences = factory.Faker('random_int', min=0, max=30000)
    needs_update = factory.Faker('boolean')
    needs_update_coincidences = factory.Faker('boolean')

    class Meta:
        model = models.NetworkSummary


class SummaryFactory(factory.DjangoModelFactory):
    station = factory.SubFactory(inforecord_factories.StationFactory)
    date = factory.Faker('past_date', start_date='2004-01-01')
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


class ConfigurationFactory(factory.DjangoModelFactory):
    source = factory.SubFactory(SummaryFactory)
    # TODO...

    class Meta:
        model = models.Configuration


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


class HistogramTypeFactory(factory.DjangoModelFactory):
    name = factory.Faker('word')
    slug = factory.Faker('slug')
    has_multiple_datasets = factory.Faker('boolean')
    bin_axis_title = factory.Faker('word')
    value_axis_title = factory.Faker('word')
    description = factory.Faker('sentence')

    class Meta:
        model = models.HistogramType


class DatasetTypeFactory(factory.DjangoModelFactory):
    name = factory.Faker('word')
    slug = factory.Faker('slug')
    x_axis_title = factory.Faker('word')
    y_axis_title = factory.Faker('word')
    description = factory.Faker('sentence')

    class Meta:
        model = models.DatasetType
