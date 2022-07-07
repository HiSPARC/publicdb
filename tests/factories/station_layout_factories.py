from datetime import date

import factory

from publicdb.station_layout import models

from .inforecords_factories import StationFactory
from .providers import DataProvider

factory.Faker.add_provider(DataProvider)


class StationLayoutFactory(factory.django.DjangoModelFactory):
    station = factory.SubFactory(StationFactory)
    active_date = factory.Faker('past_datetime', start_date=date(2004, 1, 1))
    detector_1_radius = factory.Faker('float', min=-60, max=60)
    detector_1_alpha = factory.Faker('float', min=-360, max=360)
    detector_1_height = factory.Faker('float', min=-60, max=60)
    detector_1_beta = factory.Faker('float', min=-360, max=360)
    detector_2_radius = factory.Faker('float', min=-60, max=60)
    detector_2_alpha = factory.Faker('float', min=-360, max=360)
    detector_2_height = factory.Faker('float', min=-60, max=60)
    detector_2_beta = factory.Faker('float', min=-360, max=360)
    detector_3_radius = factory.Faker('float', min=-60, max=60)
    detector_3_alpha = factory.Faker('float', min=-360, max=360)
    detector_3_height = factory.Faker('float', min=-60, max=60)
    detector_3_beta = factory.Faker('float', min=-360, max=360)
    detector_4_radius = factory.Faker('float', min=-60, max=60)
    detector_4_alpha = factory.Faker('float', min=-360, max=360)
    detector_4_height = factory.Faker('float', min=-60, max=60)
    detector_4_beta = factory.Faker('float', min=-360, max=360)

    class Meta:
        model = models.StationLayout


class StationLayoutQuarantineFactory(StationLayoutFactory):
    name = factory.Faker('name')
    email = factory.Faker('safe_email')
    # submit_date - auto add now
    email_verified = factory.Faker('boolean')
    approved = factory.Faker('boolean')
    reviewed = factory.Faker('boolean')

    hash_submit = factory.Faker('md5')
    hash_review = factory.Faker('md5')

    class Meta:
        model = models.StationLayoutQuarantine
