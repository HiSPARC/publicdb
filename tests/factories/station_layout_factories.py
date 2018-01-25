from datetime import date

import factory

from publicdb.station_layout import models

from .inforecords_factories import StationFactory


class StationLayoutFactory(factory.DjangoModelFactory):
    station = factory.SubFactory(StationFactory)
    active_date = factory.Faker('past_datetime', start_date=date(2004, 1, 1))
    detector_1_radius = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_1_alpha = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_1_height = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_1_beta = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_2_radius = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_2_alpha = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_2_height = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_2_beta = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_3_radius = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_3_alpha = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_3_height = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_3_beta = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_4_radius = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_4_alpha = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_4_height = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_4_beta = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)

    class Meta:
        model = models.StationLayout


class StationLayoutQuarantineFactory(factory.DjangoModelFactory):
    name = factory.Faker('name')
    email = factory.Faker('safe_email')
    # submit_date - auto add now
    email_verified = factory.Faker('boolean')
    approved = factory.Faker('boolean')
    reviewed = factory.Faker('boolean')

    hash_submit = factory.Faker('md5')
    hash_review = factory.Faker('md5')

    station = factory.SubFactory(StationFactory)
    active_date = factory.Faker('past_datetime', start_date=date(2004, 1, 1))
    detector_1_radius = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_1_alpha = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_1_height = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_1_beta = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_2_radius = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_2_alpha = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_2_height = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_2_beta = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_3_radius = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_3_alpha = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_3_height = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_3_beta = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_4_radius = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_4_alpha = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    detector_4_height = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    detector_4_beta = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)

    class Meta:
        model = models.StationLayoutQuarantine
