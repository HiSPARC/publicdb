from datetime import date

import factory

from publicdb.coincidences import models

from .inforrecords_factories import StationFactory
from .providers import DataProvider

factory.Faker.add_provider(DataProvider)


class EventFactory(factory.DjangoModelFactory):
    date = factory.Faker('past_date', start_date=date(2004, 1, 1))
    time = factory.Faker('time_object')
    nanoseconds = factory.Faker('random_int', min=0, max=int(1e9) - 1)
    station = factory.SubFactory(StationFactory)
    pulseheights = factory.Faker('int_list', n=4, min=0, max=4000)
    integrals = factory.Faker('int_list', n=4, min=0, max=400000)
    traces = factory.Faker('multi_int_list', detectors=4, n=2000, min=-200, max=3896)

    class Meta:
        model = models.AnalysisSession


class CoincidenceFactory(factory.DjangoModelFactory):
    date = factory.Faker('past_date', start_date=date(2004, 1, 1))
    time = factory.Faker('time_object')
    nanoseconds = factory.Faker('random_int', min=0, max=int(1e9) - 1)
    # events = many to many?! should be event -> foreignkey -> coincidence

    class Meta:
        model = models.Coincidence
