import factory

from publicdb.inforecords import models

from .providers import DataProvider, NlUrlSafeProvider, UrlSafeProvider

factory.Faker.add_provider(DataProvider)
factory.Faker.add_provider(UrlSafeProvider)
factory.Faker.add_provider(NlUrlSafeProvider, 'nl_NL')


class ProfessionFactory(factory.django.DjangoModelFactory):
    description = factory.Faker('word')

    class Meta:
        model = models.Profession
        django_get_or_create = ('description',)


class ContactInformationFactory(factory.django.DjangoModelFactory):
    street_1 = factory.Faker('street_address')
    street_2 = factory.Faker('street_address')
    postalcode = factory.Faker('postcode')
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


class ContactFactory(factory.django.DjangoModelFactory):
    profession = factory.SubFactory(ProfessionFactory)
    title = factory.Faker('word')
    first_name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    contactinformation = factory.SubFactory(ContactInformationFactory)

    class Meta:
        model = models.Contact
        django_get_or_create = ('first_name', 'surname')


class CountryFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('country_urlsafe')
    # number - set manually

    class Meta:
        model = models.Country
        django_get_or_create = ('number',)


class ClusterFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('city_urlsafe')
    # number - set manually
    # parent - set to another Cluster object
    country = factory.SubFactory(CountryFactory)
    url = 'https://www.example.com/'

    class Meta:
        model = models.Cluster
        django_get_or_create = ('number',)


class StationFactory(factory.django.DjangoModelFactory):
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


class PcFactory(factory.django.DjangoModelFactory):
    station = factory.SubFactory(StationFactory)
    name = factory.Faker('word')
    is_active = factory.Faker('boolean', chance_of_getting_true=90)
    is_test = factory.Faker('boolean', chance_of_getting_true=5)
    ip = factory.Faker('ipv4')
    notes = factory.Faker('sentence')
    # services - many to many

    class Meta:
        model = models.Pc
        django_get_or_create = ('station',)
