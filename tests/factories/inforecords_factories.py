import factory

from publicdb.inforecords import models


class ProfessionFactory(factory.DjangoModelFactory):
    description = factory.Faker('word')

    class Meta:
        model = models.Profession


class ContactInformationFactory(factory.DjangoModelFactory):
    street_1 = factory.Faker('street_address')
    street_2 = factory.Faker('street_address')
    postalcode = factory.Faker('postalcode')
    city = factory.Faker('city')
    pobox = ''
    pobox_postalcode = ''
    pobox_city = factory.Faker('city')
    phone_work = factory.Faker('phone_number')
    phone_home = factory.Faker('phone_number')
    fax = factory.Faker('phone_number')
    email_work = factory.Faker('safe_email')
    email_private = factory.Faker('safe_email')
    url = 'https://www.example.com/'

    class Meta:
        model = models.ContactInformation


class ContactFactory(factory.DjangoModelFactory):
    profession = factory.SubFactory(ProfessionFactory)
    title = factory.Faker('word')
    first_name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    contactinformation = factory.SubFactory(ContactInformationFactory)

    class Meta:
        model = models.Contact


class CountryFactory(factory.DjangoModelFactory):
    name = factory.Faker('country')
    # number - set manually

    class Meta:
        model = models.Country
        django_get_or_create = ('number',)


class ClusterFactory(factory.DjangoModelFactory):
    name = factory.Faker('city')
    # number - set manually
    # parent - set to another Cluster object
    country = factory.SubFactory(CountryFactory)
    url = 'https://www.example.com/'

    class Meta:
        model = models.Cluster
        django_get_or_create = ('number',)


class StationFactory(factory.DjangoModelFactory):
    name = factory.Faker('company')
    # number - set manually
    contactinformation = factory.SubFactory(ContactInformationFactory)
    cluster = factory.SubFactory(ClusterFactory)
    contact = factory.SubFactory(ContactFactory)
    ict_contact = factory.SubFactory(ContactFactory)
    password = factory.Faker('password', length=40, special_chars=False)
    info_page = factory.Faker('sentence')

    class Meta:
        model = models.Station
        django_get_or_create = ('number',)


class PcTypeFactory(factory.DjangoModelFactory):
    description = factory.Faker('word')
    slug = factory.Faker('slug')

    class Meta:
        model = models.PcType


class PcFactory(factory.DjangoModelFactory):
    station = factory.SubFactory(StationFactory)
    type = factory.SubFactory(PcTypeFactory)
    name = factory.Faker('word')
    is_active = factory.Faker('boolean')
    is_test = factory.Faker('boolean')
    ip = factory.Faker('ipv4')
    notes = factory.Faker('sentence')
    # services - many to many

    class Meta:
        model = models.Pc


class MonitorPulseheightThresholdsFactory(factory.DjangoModelFactory):
    station = factory.SubFactory(StationFactory)
    plate = factory.Faker('random_int', min=1, max=4)
    mpv_mean = factory.Faker('pyfloat', left_digits=3, right_digits=1, positive=True)
    mpv_sigma = factory.Faker('pyfloat', left_digits=1, right_digits=1, positive=True)
    mpv_max_allowed_drift = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)
    mpv_min_allowed_drift = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=False)

    class Meta:
        model = models.MonitorPulseheightThresholds


class MonitorServiceFactory(factory.DjangoModelFactory):
    description = factory.Faker('word')
    nagios_command = factory.Faker('word')
    is_default_service = factory.Faker('boolean')
    enable_active_checks = factory.Faker('boolean')
    min_critical = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    max_critical = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    min_warning = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    max_warning = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)

    class Meta:
        model = models.MonitorService


class EnabledServiceFactory(factory.DjangoModelFactory):
    pc = factory.SubFactory(PcFactory)
    monitor_service = factory.SubFactory(MonitorServiceFactory)
    min_critical = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    max_critical = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    min_warning = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)
    max_warning = factory.Faker('pyfloat', left_digits=2, right_digits=1, positive=True)

    class Meta:
        model = models.EnabledService
