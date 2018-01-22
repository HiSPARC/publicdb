import factory

from publicdb.updates import models


class UpdateQueueFactory(factory.DjangoModelFactory):
    slug = factory.Faker('slug')

    class Meta:
        model = models.UpdateQueue
        django_get_or_create = ('slug',)


class AdminUpdateFactory(factory.DjangoModelFactory):
    # version is based on filename
    version = factory.Faker('random_int', min=0, max=32767)
    update = factory.django.FileField(data='admin_update', filename='admin_update_v1.exe')
    queue = factory.SubFactory(UpdateQueueFactory)

    class Meta:
        model = models.AdminUpdate
        django_get_or_create = ('queue', 'version')


class UserUpdateFactory(factory.DjangoModelFactory):
    # version is based on filename
    version = factory.Faker('random_int', min=0, max=32767)
    update = factory.django.FileField(data='user_update', filename='user_update_v1.exe')
    queue = factory.SubFactory(UpdateQueueFactory)

    class Meta:
        model = models.UserUpdate
        django_get_or_create = ('queue', 'version')


class InstallerUpdateFactory(factory.DjangoModelFactory):
    # version is based on filename
    version = factory.Faker('random_int', min=0, max=32767)
    installer = factory.django.FileField(data='installer_update', filename='installer_update_v1.1.exe')
    queue = factory.SubFactory(UpdateQueueFactory)

    class Meta:
        model = models.InstallerUpdate
        django_get_or_create = ('queue', 'version')
