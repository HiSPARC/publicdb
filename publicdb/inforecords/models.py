import datetime

from xmlrpc.client import ServerProxy

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Max
from django.utils.text import slugify

from ..histograms.models import Configuration, Summary

FIRSTDATE = datetime.date(2004, 1, 1)


class Profession(models.Model):
    description = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'Profession'
        verbose_name_plural = 'Professions'

    def __str__(self):
        return self.description


class ContactInformation(models.Model):
    street_1 = models.CharField(max_length=255)
    street_2 = models.CharField(max_length=255, null=True, blank=True)
    postalcode = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    pobox = models.CharField(max_length=255, null=True, blank=True)
    pobox_postalcode = models.CharField(max_length=255, null=True, blank=True)
    pobox_city = models.CharField(max_length=255, null=True, blank=True)
    phone_work = models.CharField(max_length=255)
    phone_home = models.CharField(max_length=255, null=True, blank=True)
    fax = models.CharField(max_length=255, null=True, blank=True)
    email_work = models.EmailField()
    email_private = models.EmailField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = 'Contact information'
        verbose_name_plural = 'Contact information'
        ordering = ['city', 'street_1', 'email_work']

    def __str__(self):
        return f'{self.city} {self.street_1} {self.email_work}'

    @property
    def type(self):
        if self.contacts.exists():
            type = 'Contact'
        elif self.stations.exists():
            type = 'Station'
        else:
            type = 'no owner'
        return type

    @property
    def contact_owner(self):
        contacts = self.contacts.all()
        stations = self.stations.all()

        contact_str = []
        if contacts:
            contact_str.extend([str(contact) for contact in contacts])
        if stations:
            contact_str.extend([str(station) for station in stations])

        if contact_str:
            return ', '.join(contact_str)
        else:
            return 'no owner'


class Contact(models.Model):
    profession = models.ForeignKey(Profession, models.CASCADE, related_name='contacts')
    title = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255)
    prefix_surname = models.CharField(max_length=255, blank=True)
    surname = models.CharField(max_length=255)
    contactinformation = models.ForeignKey(ContactInformation, models.CASCADE, related_name='contacts')

    class Meta:
        verbose_name = 'contact'
        verbose_name_plural = 'contacts'
        unique_together = ('first_name', 'prefix_surname', 'surname')
        ordering = ['surname', 'first_name']

    def __str__(self):
        return self.name

    @property
    def email_work(self):
        return self.contactinformation.email_work

    @property
    def name(self):
        return f'{self.title} {self.first_name} {self.prefix_surname} {self.surname}'.replace('  ', ' ').strip()


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    number = models.IntegerField(unique=True, blank=True)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['number']

    def __str__(self):
        return self.name

    def clean(self):
        if self.number is None:
            if Country.objects.count() > 0:
                countrymax = Country.objects.aggregate(Max('number'))
                self.number = countrymax['number__max'] + 10000
            else:
                self.number = 0

        if self.number % 10000:
            raise ValidationError('Country number must be multiple of 10000')

    def last_cluster_number(self):
        clusters = self.clusters.filter(parent=None)
        if clusters:
            clustermax = clusters.aggregate(Max('number'))
            return clustermax['number__max']
        else:
            return self.number - 1000


class Cluster(models.Model):
    name = models.CharField(max_length=255, unique=True)
    number = models.IntegerField(unique=True, blank=True)
    parent = models.ForeignKey('self', models.CASCADE, null=True, blank=True, related_name='subclusters')
    country = models.ForeignKey(Country, models.CASCADE, related_name='clusters')
    url = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = 'Cluster'
        verbose_name_plural = 'Clusters'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        reload_datastore()

    def clean(self):
        if self.number is None:
            if self.parent is None:
                # New cluster
                self.number = self.country.last_cluster_number() + 1000
            else:
                # New subcluster
                self.number = self.parent.last_subcluster_number() + 100

        if self.parent is None:
            if self.number % 1000:
                raise ValidationError('Cluster number must be multiple of 1000')
            if not 0 <= (self.number - self.country.number) < 10000:
                raise ValidationError(
                    'Cluster number must be in range of '
                    f'numbers for the country ({self.country.number}, {self.country.number + 10000}).',
                )
        if self.parent is not None:
            if self.parent.parent is not None:
                raise ValidationError('Subsubclusters are not allowed')
            if self.number % 100:
                raise ValidationError('Subcluster number must be multiple of 100')
            if not 0 < (self.number - self.parent.number) < 1000:
                raise ValidationError(
                    'Subcluster number must be in range of '
                    f'numbers for the cluster ({self.parent.number}, {self.parent.number + 1000}).',
                )

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        reload_datastore()

    def main_cluster(self):
        if self.parent:
            return self.parent.main_cluster()
        else:
            return self.name

    def last_station_number(self):
        stations = self.stations.filter(number__lt=(self.number + 90))
        if stations:
            stationmax = stations.aggregate(Max('number'))
            return stationmax['number__max']
        else:
            return self.number - 1

    def last_subcluster_number(self):
        subclusters = self.subclusters.all()
        if subclusters:
            clustermax = subclusters.aggregate(Max('number'))
            return clustermax['number__max']
        else:
            return self.number


class Station(models.Model):
    name = models.CharField(max_length=255)
    number = models.IntegerField(unique=True, blank=True)
    contactinformation = models.ForeignKey(ContactInformation, models.CASCADE, related_name='stations')
    cluster = models.ForeignKey(Cluster, models.CASCADE, related_name='stations')
    contact = models.ForeignKey(Contact, models.SET_NULL, related_name='stations_contact', null=True)
    ict_contact = models.ForeignKey(Contact, models.SET_NULL, related_name='stations_ict_contact', null=True)
    password = models.CharField(max_length=255)
    info_page = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Station'
        verbose_name_plural = 'Stations'
        ordering = ['number']

    def __str__(self):
        return f'{self.number:5}: {self.name}'

    def save(self, *args, **kwargs):
        # Strip some problematic characters
        self.name = self.name.replace('"', '').replace("'", '')
        if self.number is None:
            self.number = self.cluster.last_station_number() + 1
        super().save(*args, **kwargs)
        reload_datastore()

    def clean(self):
        if self.number is None:
            self.number = self.cluster.last_station_number() + 1
        if not 0 < (self.number - self.cluster.number) < 100:
            raise ValidationError(
                'Station number must be in range of numbers for the (sub)cluster '
                f'({self.cluster.number}, {self.cluster.number + 100}).',
            )

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        reload_datastore()

    def number_of_detectors(self):
        """Get number of detectors, based on presence of Secondary electronics

        Returns 4 if no config is present to be on the safe side.

        """
        n_detectors = 0
        today = datetime.datetime.utcnow()

        try:
            config = Configuration.objects.filter(summary__station=self, timestamp__lte=today).latest()
        except Configuration.DoesNotExist:
            n_detectors = 4
        else:
            if config.secondary == -1:
                n_detectors = 2
            else:
                n_detectors = 4

        return n_detectors

    def latest_location(self, date=None):
        """Get latest valid station location

        Locations of (0, 0, 0) are excluded. If no (valid) location is
        available the coordinates returned are None.

        """
        if date is None:
            date = datetime.date.today()

        # Initialize new config with all None values.
        config = Configuration()

        try:
            summaries = Summary.objects.with_config().filter(station=self, date__lte=date).reverse()
            for summary in summaries:
                try:
                    config = (
                        Configuration.objects.filter(summary=summary).exclude(gps_latitude=0, gps_longitude=0).latest()
                    )
                except Configuration.DoesNotExist:
                    pass
                else:
                    break
        except Summary.DoesNotExist:
            pass

        return {
            'latitude': (round(config.gps_latitude, 7) if config.gps_latitude is not None else None),
            'longitude': (round(config.gps_longitude, 7) if config.gps_longitude is not None else None),
            'altitude': (round(config.gps_altitude, 2) if config.gps_altitude is not None else None),
        }


class PcType(models.Model):
    description = models.CharField(max_length=255, unique=True)
    slug = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'PC Type'
        verbose_name_plural = 'PC Types'

    def __str__(self):
        return self.description


class Pc(models.Model):
    station = models.ForeignKey(Station, models.CASCADE, related_name='pcs')
    type = models.ForeignKey(PcType, models.CASCADE, related_name='pcs')
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    is_test = models.BooleanField(default=False)
    ip = models.GenericIPAddressField(unique=True, blank=True, null=True, protocol='ipv4')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'PC and certificates'
        verbose_name_plural = 'PCs and certificates'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # slugify the short name to keep it clean
        self.name = slugify(self.name).replace('-', '').replace('_', '')
        super().save(*args, **kwargs)


def reload_datastore():
    """Reload the datastore configuration"""

    if settings.DATASTORE_PROXY is not None:
        try:
            proxy = ServerProxy(settings.DATASTORE_PROXY)
            transaction.on_commit(proxy.reload_datastore)
        except Exception:
            # FIXME logging!
            pass
