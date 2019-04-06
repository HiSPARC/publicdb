import datetime
import xmlrpclib

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Max
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from ..histograms.models import Configuration, Summary

FIRSTDATE = datetime.date(2004, 1, 1)


class Profession(models.Model):
    description = models.CharField(max_length=40, unique=True)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = 'Profession'
        verbose_name_plural = 'Professions'


class ContactInformation(models.Model):
    street_1 = models.CharField(max_length=40)
    street_2 = models.CharField(max_length=40, null=True, blank=True)
    postalcode = models.CharField(max_length=12)
    city = models.CharField(max_length=40)
    pobox = models.CharField(max_length=12, null=True, blank=True)
    pobox_postalcode = models.CharField(max_length=12, null=True, blank=True)
    pobox_city = models.CharField(max_length=40, null=True, blank=True)
    phone_work = models.CharField(max_length=20)
    phone_home = models.CharField(max_length=20, null=True, blank=True)
    fax = models.CharField(max_length=20, null=True, blank=True)
    email_work = models.EmailField()
    email_private = models.EmailField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def __unicode__(self):
        return "%s %s %s" % (self.city, self.street_1, self.email_work)

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

    def save(self, *args, **kwargs):
        super(ContactInformation, self).save(*args, **kwargs)
        reload_nagios()

    class Meta:
        verbose_name = "Contact information"
        verbose_name_plural = "Contact information"
        ordering = ['city', 'street_1', 'email_work']


class Contact(models.Model):
    profession = models.ForeignKey(Profession, models.CASCADE, related_name='contacts')
    title = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=40)
    prefix_surname = models.CharField(max_length=10, blank=True)
    surname = models.CharField(max_length=40)
    contactinformation = models.ForeignKey(ContactInformation, models.CASCADE, related_name='contacts')

    def __unicode__(self):
        return self.name

    @property
    def email_work(self):
        return self.contactinformation.email_work

    @property
    def name(self):
        return (' '.join((self.title, self.first_name, self.prefix_surname, self.surname))
                   .replace('  ', ' ')
                   .strip())

    def save(self, *args, **kwargs):
        super(Contact, self).save(*args, **kwargs)
        reload_nagios()

    class Meta:
        verbose_name = 'contact'
        verbose_name_plural = 'contacts'
        unique_together = ('first_name', 'prefix_surname', 'surname')
        ordering = ['surname', 'first_name']


class Country(models.Model):
    name = models.CharField(max_length=70, unique=True)
    number = models.IntegerField(unique=True, blank=True)

    def __unicode__(self):
        return self.name

    def clean(self):
        if self.number is None:
            if Country.objects.count() > 0:
                countrymax = Country.objects.aggregate(Max('number'))
                self.number = countrymax['number__max'] + 10000
            else:
                self.number = 0

        if self.number % 10000:
            raise ValidationError("Country number must be multiple of 10000")

    def last_cluster_number(self):
        clusters = self.clusters.filter(parent=None)
        if clusters:
            clustermax = clusters.aggregate(Max('number'))
            return clustermax['number__max']
        else:
            return self.number - 1000

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['number']


class Cluster(models.Model):
    name = models.CharField(max_length=70, unique=True)
    number = models.IntegerField(unique=True, blank=True)
    parent = models.ForeignKey('self', models.CASCADE, null=True, blank=True, related_name='subclusters')
    country = models.ForeignKey(Country, models.CASCADE, related_name='clusters')
    url = models.URLField(null=True, blank=True)

    def __unicode__(self):
        return self.name

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
                raise ValidationError("Cluster number must be multiple of 1000")
            if not 0 <= (self.number - self.country.number) < 10000:
                raise ValidationError("Cluster number must be in range of "
                                      "numbers for the country (%d, %d)." %
                                      (self.country.number, self.country.number + 10000))
        if self.parent is not None:
            if self.parent.parent is not None:
                raise ValidationError("Subsubclusters are not allowed")
            if self.number % 100:
                raise ValidationError("Subcluster number must be multiple of 100")
            if not 0 < (self.number - self.parent.number) < 1000:
                raise ValidationError("Subcluster number must be in range of "
                                      "numbers for the cluster (%d, %d)." %
                                      (self.parent.number, self.parent.number + 1000))

    def save(self, *args, **kwargs):
        super(Cluster, self).save(*args, **kwargs)
        reload_datastore()

    def delete(self, *args, **kwargs):
        super(Cluster, self).delete(*args, **kwargs)
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

    class Meta:
        verbose_name = 'Cluster'
        verbose_name_plural = 'Clusters'
        ordering = ['name']


class Station(models.Model):
    name = models.CharField(max_length=70)
    number = models.IntegerField(unique=True, blank=True)
    contactinformation = models.ForeignKey(ContactInformation, models.CASCADE, related_name='stations')
    cluster = models.ForeignKey(Cluster, models.CASCADE, related_name='stations')
    contact = models.ForeignKey(Contact, models.SET_NULL, related_name='stations_contact', null=True)
    ict_contact = models.ForeignKey(Contact, models.SET_NULL, related_name='stations_ict_contact', null=True)
    password = models.CharField(max_length=40)
    info_page = models.TextField(blank=True)

    def __unicode__(self):
        return '%5d: %s' % (self.number, self.name)

    def clean(self):
        if self.number is None:
            self.number = self.cluster.last_station_number() + 1
        if not 0 < (self.number - self.cluster.number) < 100:
            raise ValidationError("Station number must be in range of "
                                  "numbers for the (sub)cluster (%d, %d)." %
                                  (self.cluster.number,
                                   self.cluster.number + 100))

    def save(self, *args, **kwargs):
        # Strip some problematic characters
        self.name = self.name.replace('"', '').replace("'", '')
        if self.number is None:
            self.number = self.cluster.last_station_number() + 1
        super(Station, self).save(*args, **kwargs)
        reload_datastore()

    def delete(self, *args, **kwargs):
        super(Station, self).delete(*args, **kwargs)
        reload_datastore()

    def number_of_detectors(self):
        """Get number of detectors, based on presence of Slave electronics

        Returns 4 if no config is present to be on the safe side.

        """
        n_detectors = 0
        today = datetime.datetime.utcnow()

        try:
            config = (Configuration.objects.filter(summary__station=self, timestamp__lte=today).latest())
        except Configuration.DoesNotExist:
            n_detectors = 4
        else:
            if config.slave == -1:
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
                    config = (Configuration.objects
                                           .filter(summary=summary)
                                           .exclude(gps_latitude=0, gps_longitude=0)
                                           .latest())
                except Configuration.DoesNotExist:
                    pass
                else:
                    break
        except Summary.DoesNotExist:
            pass

        return {'latitude': (round(config.gps_latitude, 7) if config.gps_latitude is not None else None),
                'longitude': (round(config.gps_longitude, 7) if config.gps_longitude is not None else None),
                'altitude': (round(config.gps_altitude, 2) if config.gps_altitude is not None else None)}

    class Meta:
        verbose_name = 'Station'
        verbose_name_plural = 'Stations'
        ordering = ['number']


class PcType(models.Model):
    description = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=20)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = 'PC Type'
        verbose_name_plural = 'PC Types'


class Pc(models.Model):
    station = models.ForeignKey(Station, models.CASCADE, related_name='pcs')
    type = models.ForeignKey(PcType, models.CASCADE, related_name='pcs')
    name = models.CharField(max_length=40, unique=True)
    is_active = models.BooleanField(default=False)
    is_test = models.BooleanField(default=False)
    ip = models.GenericIPAddressField(unique=True, blank=True, null=True, protocol='IPV4')
    notes = models.TextField(blank=True)
    services = models.ManyToManyField('MonitorService', through='EnabledService')

    def __unicode__(self):
        return self.name

    def keys(self):
        return mark_safe(
            '<a href="{url}">Certificate {name}</a>'
            .format(url=reverse('keys', kwargs={'host': self.name}), name=self.name)
        )
    keys.short_description = 'Certificates'

    def url(self):
        if self.type.slug == 'admin':
            return ''
        else:
            return mark_safe(
                '<a href="vnc://s{number}.his">s{number}.his</a>'
                .format(number=self.station.number)
            )
    url.short_description = 'VNC URL'

    class Meta:
        verbose_name = 'PC and certificates'
        verbose_name_plural = 'PCs and certificates'
        ordering = ['name']

    def generate_ip_address(self, ipaddress):
        """Generate new IP address

        Increments given IP address by 1.
        Source: http://code.activestate.com/recipes/65219/

        """
        hexn = ''.join(["%02X" % long(i) for i in ipaddress.split('.')])
        n = long(hexn, 16) + 1

        d = 256 * 256 * 256
        q = []
        while d > 0:
            m, n = divmod(n, d)
            q.append(str(m))
            d = d / 256

        return '.'.join(q)

    def save(self, *args, **kwargs):
        # slugify the short name to keep it clean
        self.name = unicode(slugify(self.name)).replace('-', '').replace('_', '')

        if self.id:
            super(Pc, self).save(*args, **kwargs)
        else:
            if self.type.slug == "admin":
                try:
                    last_ip = Pc.objects.filter(type__slug="admin").latest('id').ip
                except Pc.DoesNotExist:
                    # Initial Admin IP
                    last_ip = '172.16.66.1'
            else:
                try:
                    last_ip = Pc.objects.exclude(type__slug="admin").latest('id').ip
                except Pc.DoesNotExist:
                    # Initial station IP
                    last_ip = '194.171.82.1'
            self.ip = self.generate_ip_address(last_ip)

            # First create keys, then issue final save
            create_keys(self)

            super(Pc, self).save(*args, **kwargs)

            # FIXME this doesn't check for preselected services
            self.install_default_services()
        update_aliases()

    def delete(self, *args, **kwargs):
        super(Pc, self).delete(*args, **kwargs)
        update_aliases()

    def install_default_services(self):
        if self.type.slug != "admin":
            for service in MonitorService.objects.filter(is_default_service=True):
                EnabledService(pc=self, monitor_service=service).save()


class MonitorService(models.Model):
    description = models.CharField(max_length=40, unique=True)
    nagios_command = models.CharField(max_length=70)
    is_default_service = models.BooleanField(default=False)
    enable_active_checks = models.BooleanField(default=True)
    min_critical = models.FloatField(null=True, blank=True)
    max_critical = models.FloatField(null=True, blank=True)
    min_warning = models.FloatField(null=True, blank=True)
    max_warning = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = 'Monitor Service'
        verbose_name_plural = 'Monitor Services'
        ordering = ['description']

    def save(self, *args, **kwargs):
        super(MonitorService, self).save(*args, **kwargs)

        if self.is_default_service:
            for pc in Pc.objects.exclude(type__slug="admin"):
                try:
                    service = EnabledService.objects.get(pc=pc, monitor_service=self)
                except EnabledService.DoesNotExist:
                    service = EnabledService(pc=pc, monitor_service=self)
                    service.save()


class EnabledService(models.Model):
    pc = models.ForeignKey(Pc, models.CASCADE, related_name='enabled_services')
    monitor_service = models.ForeignKey(MonitorService, models.CASCADE, related_name='enabled_services')
    min_critical = models.FloatField(null=True, blank=True)
    max_critical = models.FloatField(null=True, blank=True)
    min_warning = models.FloatField(null=True, blank=True)
    max_warning = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return '%s - %s' % (self.pc, self.monitor_service)

    class Meta:
        verbose_name = 'Enabled Service'
        verbose_name_plural = 'Enabled Services'
        ordering = ['pc', 'monitor_service']

    def save(self, *args, **kwargs):
        super(EnabledService, self).save(*args, **kwargs)
        reload_nagios()

    def delete(self, *args, **kwargs):
        super(EnabledService, self).delete(*args, **kwargs)
        reload_nagios()


def create_keys(pc):
    """Create VPN keys for the given Pc"""

    if settings.VPN_PROXY is not None:
        proxy = xmlrpclib.ServerProxy(settings.VPN_PROXY)
        proxy.create_key(pc.name, pc.type.slug, pc.ip)


def update_aliases():
    """Update VPN aliases"""

    if settings.VPN_PROXY is not None:
        proxy = xmlrpclib.ServerProxy(settings.VPN_PROXY)
        aliases = [('s%d' % x.station.number, x.ip) for x in Pc.objects.all()]
        aliases.extend([(x.name, x.ip) for x in Pc.objects.all()])
        proxy.register_hosts_ip(aliases)
        reload_nagios()


def reload_nagios():
    """Reload the nagios configuration"""

    if settings.VPN_PROXY is not None:
        try:
            proxy = xmlrpclib.ServerProxy(settings.VPN_PROXY)
            transaction.on_commit(proxy.reload_nagios)
        except Exception:
            # FIXME logging!
            pass


def reload_datastore():
    """Reload the datastore configuration"""

    if settings.DATASTORE_PROXY is not None:
        try:
            proxy = xmlrpclib.ServerProxy(settings.DATASTORE_PROXY)
            transaction.on_commit(proxy.reload_datastore)
        except Exception:
            # FIXME logging!
            pass
