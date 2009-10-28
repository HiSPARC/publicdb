from django.db import models
from eventwarehouse import update_station_password, remove_station_password

class Contactposition(models.Model):
    description = models.CharField(max_length=40, unique=True)

    def __unicode__(self):
        return self.description

class Contact(models.Model):
    location = models.ForeignKey('Location', related_name='contacts',
                                 null=True, blank=True)
    contactposition = models.ForeignKey(Contactposition)
    title = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=40)
    prefix_last_name = models.CharField(max_length=10, blank=True)
    last_name = models.CharField(max_length=40)
    url = models.URLField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_work = models.CharField(max_length=20, null=True, blank=True)
    phone_home = models.CharField(max_length=20, null=True, blank=True)

    def __unicode__(self):
        return "%s %s %s %s" % (self.title, self.first_name,
                                self.prefix_last_name, self.last_name)

    class Meta:
        unique_together = [('first_name', 'prefix_last_name', 'last_name')]
        ordering = ('last_name', 'first_name')

class Organization(models.Model):
    name = models.CharField(max_length=40, unique=True)
    url = models.URLField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)

class Cluster(models.Model):
    name = models.CharField(max_length=70, unique=True)
    country = models.CharField(max_length=40)
    contact = models.ForeignKey(Contact, null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('country', 'name')

class LocationStatus(models.Model):
    description = models.CharField(max_length=40, unique=True)
    
    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name_plural = 'Location Status'

class Location(models.Model):
    name = models.CharField(max_length=70, unique=True)
    organization = models.ForeignKey(Organization)
    cluster = models.ForeignKey(Cluster)
    locationstatus = models.ForeignKey(LocationStatus)
    address = models.CharField(max_length=40, null=True, blank=True)
    postalcode = models.CharField(max_length=6, null=True, blank=True)
    pobox = models.CharField(max_length=9, null=True, blank=True)
    pobox_postalcode = models.CharField(max_length=6, null=True, blank=True)
    pobox_city = models.CharField(max_length=40, null=True, blank=True)
    city = models.CharField(max_length=40)
    phone = models.CharField(max_length=20, null=True, blank=True)
    fax = models.CharField(max_length=20, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)

class Station(models.Model):
    location = models.ForeignKey(Location)
    contact = models.ForeignKey(Contact, null=True, blank=True)
    number = models.IntegerField(unique=True)
    password = models.CharField(max_length=40)

    def __unicode__(self):
        return '%s - %s' % (self.number, self.location)

    def cluster(self):
        return self.location.cluster

    def save(self, force_insert=False, force_update=False):
        update_station_password(self.number, self.password)
        super(Station, self).save(force_insert, force_update)

    def delete(self):
        remove_station_password(self.number)
        super(Station, self).delete()

    class Meta:
        ordering = ('number',)

class DetectorStatus(models.Model):
    description = models.CharField(max_length=40, unique=True)
    
    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name_plural = 'Detector Status'

class DetectorHisparc(models.Model):
    station = models.ForeignKey(Station)
    status = models.ForeignKey(DetectorStatus)
    startdate = models.DateField()
    enddate = models.DateField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    direction = models.FloatField(null=True, blank=True)
    translation_perp = models.FloatField(null=True, blank=True)
    translation_long = models.FloatField(null=True, blank=True)
    scintillator_1_perp = models.FloatField(null=True, blank=True)
    scintillator_1_long = models.FloatField(null=True, blank=True)
    scintillator_1_angle = models.FloatField(null=True, blank=True)
    scintillator_2_perp = models.FloatField(null=True, blank=True)
    scintillator_2_long = models.FloatField(null=True, blank=True)
    scintillator_2_angle = models.FloatField(null=True, blank=True)
    scintillator_3_perp = models.FloatField(null=True, blank=True)
    scintillator_3_long = models.FloatField(null=True, blank=True)
    scintillator_3_angle = models.FloatField(null=True, blank=True)
    scintillator_4_perp = models.FloatField(null=True, blank=True)
    scintillator_4_long = models.FloatField(null=True, blank=True)
    scintillator_4_angle = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.station)

    class Meta:
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

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name_plural = 'PC Type'

class Pc(models.Model):
    station = models.ForeignKey(Station)
    type = models.ForeignKey(PcType)
    name = models.CharField(max_length=40, unique=True)
    ip = models.IPAddressField(unique=True, blank=True)
    notes = models.TextField(blank=True)
    services = models.ManyToManyField('MonitorService',
                                      through='EnabledService')
    
    def __unicode__(self):
        return self.name

    def certificaat(self):
        return "<a target=_blank href=http://vpn.hisparc.nl/certificaat/" \
               "genereer/%s/%s.zip>Certificaat %s</a>" % (self.type_id,
                                                          self.name, self.name)
    certificaat.short_description = 'Certificaten'
    certificaat.allow_tags = True

    def url(self):
        if self.type.description == 'Admin PC':
            return ''
        else:
            return '<a href=vnc://%s.his>%s.his</a>' % (self.name, self.name)
    url.short_description = 'VPN URL'
    url.allow_tags = True

    class Meta:
        verbose_name_plural = 'PC en Certificaten'
        ordering = ('name',)

    def ipAdresGenereer(self,ipadres):
        # bron: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65219
        hexn = ''.join(["%02X" % long(i) for i in ipadres.split('.')])
        n = long(hexn, 16) + 1

        d = 256 * 256 * 256
        q = []
        while d > 0:
                m,n = divmod(n,d)
                q.append(str(m))
                d = d/256

        return '.'.join(q)

    def save(self, force_insert=False, force_update=False):
        if self.id:
            super(Pc, self).save(force_insert, force_update)
        else:
            if self.type.description == "Admin PC":
                vorigip = Pc.objects.filter(type__description="Admin PC").\
                          latest('id').ip
            else:
                vorigip = Pc.objects.exclude(type__description="Admin PC").\
                          latest('id').ip
            self.ip = self.ipAdresGenereer(vorigip)

            super(Pc, self).save(force_insert, force_update)
            self.install_default_services()

    def install_default_services(self):
        if self.type.description != "Admin PC":
            for service in MonitorService.objects. \
                            filter(is_default_service=True):
                EnabledService(pc=self, monitor_service=service).save()

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

    def save(self, force_insert=False, force_update=False):
        super(MonitorService, self).save(force_insert, force_update)

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
	ordering = ('pc', 'monitor_service')
