from datetime import date

import factory

from publicdb.analysissessions import models

from .coincidences_factories import CoincidenceFactory
from .inforecords_factories import ClusterFactory
from .providers import DataProvider

factory.Faker.add_provider(DataProvider)


class SessionRequestFactory(factory.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    sur_name = factory.Faker('last_name')
    email = factory.Faker('safe_email')
    school = factory.Faker('company')
    cluster = factory.SubFactory(ClusterFactory)
    events_to_create = factory.Faker('random_int', min=0, max=10000)
    events_created = factory.Faker('random_int', min=0, max=10000)
    start_date = factory.Faker('past_date', start_date=date(2004, 1, 1))
    mail_send = factory.Faker('boolean')
    session_confirmed = factory.Faker('boolean')
    session_pending = factory.Faker('boolean')
    session_created = factory.Faker('boolean')
    url = factory.Faker('word')
    sid = factory.Faker('slug')
    pin = factory.Faker('numerify', text='####')

    class Meta:
        model = models.SessionRequest


class NewSessionRequestFactory(SessionRequestFactory):
    events_created = 0
    session_confirmed = False
    session_pending = False
    session_created = False


class AnalysisSessionFactory(factory.DjangoModelFactory):
    session_request = factory.SubFactory(SessionRequestFactory)
    title = factory.Faker('word')
    slug = factory.Faker('slug')
    # hash - Automatically generated on save
    pin = factory.Faker('numerify', text='####')
    starts = factory.Faker('past_datetime')
    ends = factory.Faker('future_datetime')

    class Meta:
        model = models.AnalysisSession
        django_get_or_create = ('slug',)


class StudentFactory(factory.DjangoModelFactory):
    session = factory.SubFactory(AnalysisSessionFactory)
    name = factory.Faker('first_name')

    class Meta:
        model = models.Student


class AnalyzedCoincidenceFactory(factory.DjangoModelFactory):
    session = factory.SubFactory(AnalysisSessionFactory)
    coincidence = factory.SubFactory(CoincidenceFactory)
    student = factory.SubFactory(StudentFactory)
    is_analyzed = factory.Faker('boolean')
    core_position_x = factory.Faker('float', min=-200, max=200)
    core_position_y = factory.Faker('float', min=-200, max=200)
    log_energy = factory.Faker('float', min=11, max=22)
    theta = factory.Faker('float', min=0, max=90)
    phi = factory.Faker('float', min=-360, max=360)
    error_estimate = factory.Faker('float', min=0, max=200)

    class Meta:
        model = models.AnalyzedCoincidence
