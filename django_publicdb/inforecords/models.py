from django.db import models
from django.db.models import Max
from django.core.urlresolvers import reverse
import xmlrpclib

from django.conf import settings

import datetime


class Profession(models.Model):
    description = models.CharField(max_length=40, unique=True)

    def __unicode__(self):
        return self.description


class Contact(models.Model):
    profession = models.ForeignKey(Profession)
    title = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=40)
    prefix_surname = models.CharField(max_length=10, blank=True)
    surname = models.CharField(max_length=40)
    contactinformation = models.ForeignKey('ContactInformation',
                                           related_name='contacts')

    def __unicode__(self):
        return "%s %s %s %s" % (self.title, self.first_name,
                                self.prefix_surname, self.surname)

    def email_work(self):
        return self.contactinformation.email_work
    email_work = property(email_work)

    def name(self):
        return "%s %s %s %s" % (self.title, self.first_name,
                                self.prefix_surname, self.surname)
    name = property(name)

    def save(self, *args, **kwargs):
        super(Contact, self).save(*args, **kwargs)
        reload_nagios()

    class Meta:
        unique_together = [('first_name', 'prefix_surname', 'surname')]
        ordering = ('surname', 'first_name')


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

    def type(self):
        if self.contacts.all():
           type = 'Contact'
        elif self.stations.all():
           type = 'Station'
        else:
           type = 'no owner'
        return type
    type = property(type)

    def contact_owner(self):
        contacts = self.contacts.all()
        stations = self.stations.all()

        contact_str = []
        if contacts:
            contact_str.extend([contact.name for contact in contacts])
        if stations:
            contact_str.extend(['%s (%d)' % (station.name, station.number)
                                for station in stations])
        return ', '.join(contact_str)

        if contacts:
            contact_owner = self.contacts.get().name
        elif self.stations.all():
           contact_owner = self.stations.all()[0].name
        else:
           contact_owner = 'no owner'
        return contact_owner
    contact_owner = property(contact_owner)

    def save(self, *args, **kwargs):
        super(ContactInformation, self).save(*args, **kwargs)
        reload_nagios()

    class Meta:
        ordering = ['city', 'street_1', 'email_work']
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"


class Cluster(models.Model):
    name = models.CharField(max_length=70, unique=True)
    number = models.IntegerField(unique=True,blank=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='children')
    country = models.ForeignKey('Country', related_name='clusters')
    url = models.URLField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.number is None:
           if self.parent is None:
              self.number = self.country.last_cluster_number() + 1000
           else:
              self.number = self.parent.last_cluster_number() + 100
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
        stations=self.stations.filter(number__lt=(self.number + 90))
        if stations:
            stationmax=stations.aggregate(Max('number'))
            return stationmax['number__max']
        else:
            return self.number - 1

    def last_cluster_number(self):
        clusters=self.children.all()
        if clusters:
            clustermax=clusters.aggregate(Max('number'))
            return clustermax['number__max']
        else:
            return self.number

    class Meta:
        ordering = ('name',)


class Station(models.Model):
    name = models.CharField(max_length=70)
    number = models.IntegerField(unique=True, blank=True)
    contactinformation = models.ForeignKey('ContactInformation',
                                           related_name='stations')
    cluster = models.ForeignKey('Cluster', related_name='stations')
    contact = models.ForeignKey(Contact, related_name='stations_contact',
                                null=True)
    ict_contact = models.ForeignKey(Contact,
                                    related_name='stations_ict_contact',
                                    null=True)
    password = models.CharField(max_length=40)
    info_page = models.TextField(blank=True)

    def __unicode__(self):
        return '%5d: %s' % (self.number, self.name)

    def save(self, *args, **kwargs):
        if self.number is None:
            self.number = self.cluster.last_station_number() + 1
        new = self.pk is None
        super(Station, self).save(*args, **kwargs)
        if new:
            # New station, so create a DetectorHisparc object
            dh = DetectorHisparc(station=self, startdate=datetime.date.today())
            dh.save()
        reload_datastore()

    def delete(self, *args, **kwargs):
        super(Station, self).delete(*args, **kwargs)
        reload_datastore()

    def number_of_detectors(self):
        from django_publicdb.histograms.models import Configuration

        n_detectors = 0
        today = datetime.datetime.utcnow()

        config = (Configuration.objects.filter(source__station=self,
                                               timestamp__lte=today)
                                       .latest('timestamp'))

        if config.slave() == 'no slave':
            n_detectors = 2
        else:
            n_detectors = 4

        return n_detectors

    class Meta:
        ordering = ('number',)


class Country(models.Model):
    name = models.CharField(max_length=40, unique=True)
    number = models.IntegerField(unique=True, blank=True)

    def __unicode__(self):
        return self.name

    def last_cluster_number(self):
        clusters = self.clusters.filter(parent=None)
        if clusters:
            clustermax = clusters.aggregate(Max('number'))
            return clustermax['number__max']
        else:
            return self.number - 1000

    class Meta:
        verbose_name_plural = "Countries"

    def save(self, *args, **kwargs):
        if self.number is None:
            if Country.objects.count() > 0:
                countrymax = Country.objects.aggregate(Max('number'))
                self.number = countrymax['number__max'] + 10000
            else:
                self.number = 0
        super(Country, self).save(*args, **kwargs)


class DetectorHisparc(models.Model):
    station = models.ForeignKey(Station)
    startdate = models.DateField()
    enddate = models.DateField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    direction = models.FloatField(null=True, blank=True)
    translation_perp = models.FloatField(null=True, blank=True)
    translation_long = models.FloatField(null=True, blank=True)
    scintillator_1_alpha = models.FloatField(null=True, blank=True)
    scintillator_1_beta = models.FloatField(null=True, blank=True)
    scintillator_1_radius = models.FloatField(null=True, blank=True)
    scintillator_1_height = models.FloatField(null=True, blank=True)
    scintillator_2_alpha = models.FloatField(null=True, blank=True)
    scintillator_2_beta = models.FloatField(null=True, blank=True)
    scintillator_2_radius = models.FloatField(null=True, blank=True)
    scintillator_2_height = models.FloatField(null=True, blank=True)
    scintillator_3_alpha = models.FloatField(null=True, blank=True)
    scintillator_3_beta = models.FloatField(null=True, blank=True)
    scintillator_3_radius = models.FloatField(null=True, blank=True)
    scintillator_3_height = models.FloatField(null=True, blank=True)
    scintillator_4_alpha = models.FloatField(null=True, blank=True)
    scintillator_4_beta = models.FloatField(null=True, blank=True)
    scintillator_4_radius = models.FloatField(null=True, blank=True)
    scintillator_4_height = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.station)

    class Meta:
        unique_together = [('station', 'startdate')]
        verbose_name_plural = 'Detector HiSPARC'
        ordering = ('station__number',)


class ElectronicsType(models.Model):
    description = models.CharField(max_length=40, unique=True)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name_plural = 'Electronics Type'
        ordering = ('description',)


class ElectronicsStatus(models.Model):
    description = models.CharField(max_length=40, unique=True)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name_plural = 'Electronics Status'


class ElectronicsBatch(models.Model):
    type = models.ForeignKey(ElectronicsType)
    number = models.IntegerField(unique=True)
    notes = models.TextField()

    def __unicode__(self):
        return '%s: %s' % (self.type, self.number)

    class Meta:
        verbose_name_plural = 'Electronics Batch'
        ordering = ('type', 'number')


class Electronics(models.Model):
    station = models.ForeignKey(Station)
    type = models.ForeignKey(ElectronicsType)
    status = models.ForeignKey(ElectronicsStatus)
    startdate = models.DateField()
    enddate = models.DateField(null=True, blank=True)
    batch = models.ForeignKey(ElectronicsBatch)
    serial = models.IntegerField()
    is_master = models.BooleanField()
    has_gps = models.BooleanField()
    notes = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return '%s / %s' % (self.batch, self.serial)

    class Meta:
        verbose_name_plural = 'Electronics'
        ordering = ('batch', 'serial')


class PcType(models.Model):
    description = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=20)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name_plural = 'PC Type'


class Pc(models.Model):
    station = models.ForeignKey(Station)
    type = models.ForeignKey(PcType)
    name = models.CharField(max_length=40, unique=True)
    is_active = models.BooleanField(default=False)
    is_test = models.BooleanField(default=False)
    ip = models.IPAddressField(unique=True, blank=True)
    notes = models.TextField(blank=True)
    services = models.ManyToManyField('MonitorService',
                                      through='EnabledService')

    def __unicode__(self):
        return self.name

    def keys(self):
        return ("<a href=%s>Certificate %s</a>" %
                (reverse('django_publicdb.inforecords.views.keys',
                         args=[self.name]),
                 self.name))

    keys.short_description = 'Certificates'
    keys.allow_tags = True

    def url(self):
        if self.type.description == 'Admin PC':
            return ''
        else:
            return '<a href=vnc://%s.his>%s.his</a>' % (self.name, self.name)
    url.short_description = 'VNC URL'
    url.allow_tags = True

    class Meta:
        verbose_name_plural = 'PC and Certificates'
        ordering = ('name',)

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
        self.name = self.name.lower().replace(' ', '')
        proxy = xmlrpclib.ServerProxy(settings.VPN_PROXY)

        if self.id:
            super(Pc, self).save(*args, **kwargs)
        else:
            if self.type.description == "Admin PC":
                last_ip = (Pc.objects.filter(type__description="Admin PC")
                                     .latest('id').ip)
            else:
                last_ip = (Pc.objects.exclude(type__description="Admin PC")
                                     .latest('id').ip)
            self.ip = self.generate_ip_address(last_ip)

            # First create keys, then issue final save
            proxy.create_key(self.name, self.type.slug, self.ip)
            super(Pc, self).save(*args, **kwargs)

            #FIXME this doesn't check for preselected services
            self.install_default_services()

        aliases = [('s%d' % x.station.number, x.ip) for x in Pc.objects.all()]
        aliases.extend([(x.name, x.ip) for x in Pc.objects.all()])
        proxy.register_hosts_ip(aliases)
        proxy.reload_nagios()

    def delete(self, *args, **kwargs):
        super(Pc, self).delete(*args, **kwargs)
        proxy = xmlrpclib.ServerProxy(settings.VPN_PROXY)
        aliases = [('s%d' % x.station.number, x.ip) for x in Pc.objects.all()]
        aliases.extend([(x.name, x.ip) for x in Pc.objects.all()])
        proxy.register_hosts_ip(aliases)
        proxy.reload_nagios()

    def install_default_services(self):
        if self.type.description != "Admin PC":
            for service in MonitorService.objects. \
                            filter(is_default_service=True):
                EnabledService(pc=self, monitor_service=service).save()


class MonitorPulseheightThresholds(models.Model):
    station = models.ForeignKey('Station')
    plate = models.IntegerField()

    mpv_mean = models.FloatField()
    mpv_sigma = models.FloatField()
    mpv_max_allowed_drift = models.FloatField()
    mpv_min_allowed_drift = models.FloatField()

    class Meta:
        verbose_name_plural = "Pulseheight thresholds for Nagios monitoring"


class MonitorService(models.Model):
    description = models.CharField(max_length=40, unique=True)
    nagios_command = models.CharField(max_length=70)
    is_default_service = models.BooleanField()
    enable_active_checks = models.BooleanField(default=True)
    min_critical = models.FloatField(null=True, blank=True)
    max_critical = models.FloatField(null=True, blank=True)
    min_warning = models.FloatField(null=True, blank=True)
    max_warning = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name_plural = 'Monitor Services'
        ordering = ('description',)

    def save(self, *args, **kwargs):
        super(MonitorService, self).save(*args, **kwargs)

        if self.is_default_service:
            for pc in Pc.objects.exclude(type__description="Admin PC"):
                try:
                    service = EnabledService.objects.get(pc=pc,
                                                         monitor_service=self)
                except EnabledService.DoesNotExist:
                    service = EnabledService(pc=pc, monitor_service=self)
                    service.save()


class EnabledService(models.Model):
    pc = models.ForeignKey(Pc)
    monitor_service = models.ForeignKey(MonitorService)
    min_critical = models.FloatField(null=True, blank=True)
    max_critical = models.FloatField(null=True, blank=True)
    min_warning = models.FloatField(null=True, blank=True)
    max_warning = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return '%s - %s' % (self.pc, self.monitor_service)

    class Meta:
        verbose_name_plural = 'Enabled Services'
        ordering = ('pc', 'monitor_service')

    def save(self, *args, **kwargs):
        super(EnabledService, self).save(*args, **kwargs)
        reload_nagios()

    def delete(self, *args, **kwargs):
        super(EnabledService, self).delete(*args, **kwargs)
        reload_nagios()


def reload_nagios():
    """Reload the nagios configuration"""

    try:
        proxy = xmlrpclib.ServerProxy(settings.VPN_PROXY)
        proxy.reload_nagios()
    except:
        #FIXME logging!
        pass


def reload_datastore():
    """Reload the datastore configuration"""

    try:
        proxy = xmlrpclib.ServerProxy(settings.DATASTORE_PROXY)
        proxy.reload_datastore()
    except:
        #FIXME logging!
        pass
