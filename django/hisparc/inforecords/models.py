from django.db import models

class Contactposition(models.Model):
    description = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.description

    class Admin:
        pass

class Contact(models.Model):
    location = models.ForeignKey('Location', related_name='contacts', null=True, blank=True)
    contactposition = models.ForeignKey(Contactposition)
    title = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=40)
    prefix_last_name = models.CharField(max_length=10, blank=True)
    last_name = models.CharField(max_length=40)
    url = models.URLField(null=True, blank=True)
    email = models.EmailField()
    phone_work = models.PhoneNumberField(null=True, blank=True)
    phone_home = models.PhoneNumberField(null=True, blank=True)

    def __str__(self):
        return '%s %s %s %s' % (self.title, self.first_name, self.prefix_last_name, self.last_name)

    class Meta:
        unique_together = [('first_name', 'prefix_last_name', 'last_name')]

    class Admin:
        list_display = ('__str__', 'contactposition', 'email', 'phone_work', 'url')
        list_filter = ('contactposition',)
        ordering = ('last_name', 'first_name')

class Organization(models.Model):
    name = models.CharField(max_length=40, unique=True)
    contact = models.ForeignKey(Contact, null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Admin:
        ordering = ('name',)

class Cluster(models.Model):
    name = models.CharField(max_length=70, unique=True)
    country = models.CharField(max_length=40)
    contact = models.ForeignKey(Contact, null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Admin:
        list_display = ('name', 'country')
        list_filter = ('country',)
        ordering = ('country', 'name')


class LocationStatus(models.Model):
    description = models.CharField(max_length=40, unique=True)
    
    def __str__(self):
        return self.description

    class Admin:
        pass

class Location(models.Model):
    name = models.CharField(max_length=70, unique=True)
    organization = models.ForeignKey(Organization)
    cluster = models.ForeignKey(Cluster)
    contact = models.ForeignKey(Contact, related_name='locations', null=True, blank=True)
    locationstatus = models.ForeignKey(LocationStatus)
    address = models.CharField(max_length=40)
    postalcode = models.CharField(max_length=6)
    pobox = models.CharField(max_length=9, null=True, blank=True)
    pobox_postalcode = models.CharField(max_length=6, null=True, blank=True)
    pobox_city = models.CharField(max_length=40, null=True, blank=True)
    city = models.CharField(max_length=40)
    country = models.CharField(max_length=40)
    phone = models.PhoneNumberField(null=True, blank=True)
    fax = models.PhoneNumberField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    def __str__(self):
        return self.name

    class Admin:
        list_display = ('name', 'organization', 'cluster')
        list_filter = ('cluster',)
        ordering = ('name',)

class Station(models.Model):
    location = models.ForeignKey(Location)
    contact = models.ForeignKey(Contact, null=True, blank=True)
    number = models.IntegerField(unique=True)

    def __str__(self):
        return '%s - %s' % (self.number, self.location)

    def cluster(self):
        return self.location.cluster

    class Admin:
        list_display = ('number', 'location', 'cluster')
        ordering = ('number',)

class DetectorStatus(models.Model):
    description = models.CharField(max_length=40, unique=True)
    
    def __str__(self):
        return self.description

    class Admin:
        pass

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
    scintillator_2_perp = models.FloatField(null=True, blank=True)
    scintillator_2_long = models.FloatField(null=True, blank=True)
    scintillator_3_perp = models.FloatField(null=True, blank=True)
    scintillator_3_long = models.FloatField(null=True, blank=True)
    scintillator_4_perp = models.FloatField(null=True, blank=True)
    scintillator_4_long = models.FloatField(null=True, blank=True)
    password = models.CharField(max_length=40)

    def __str__(self):
        return str(self.station)

    class Admin:
        list_display = ('__str__', 'status')
        ordering = ('station',)

class ElectronicsType(models.Model):
    description = models.CharField(max_length=40, unique=True)
    
    def __str__(self):
        return self.description

    class Admin:
        pass

class ElectronicsStatus(models.Model):
    description = models.CharField(max_length=40, unique=True)
    
    def __str__(self):
        return self.description

    class Admin:
        pass

class ElectronicsBatch(models.Model):
    type = models.ForeignKey(ElectronicsType)
    number = models.IntegerField(unique=True)
    notes = models.TextField()

    def __str__(self):
        return '%s: %s' % (self.type, self.number)

    class Admin:
        pass

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

    def __str__(self):
        return '%s / %s' % (self.batch, self.serial)

    class Admin:
        pass

class PcType(models.Model):
    description = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.description

    class Admin:
        pass

class Pc(models.Model):
    station = models.ForeignKey(Station)
    type = models.ForeignKey(PcType)
    name = models.CharField(max_length=40, unique=True)
    ip = models.IPAddressField(unique=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

    class Admin:
        pass

class MonitorService(models.Model):
    description = models.CharField(max_length=40, unique=True)
    nagios_command = models.CharField(max_length=70)
    min_critical = models.FloatField(null=True, blank=True)
    max_critical = models.FloatField(null=True, blank=True)
    min_warning = models.FloatField(null=True, blank=True)
    max_warning = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.description

    class Admin:
        pass

class PcMonitorService(models.Model):
    pc = models.ForeignKey(Pc)
    monitor_service = models.ForeignKey(MonitorService)
    override_min_critical = models.FloatField(null=True, blank=True)
    override_max_critical = models.FloatField(null=True, blank=True)
    override_min_warning = models.FloatField(null=True, blank=True)
    override_max_warning = models.FloatField(null=True, blank=True)

    def __str__(self):
        return '%s - %s' % (self.pc, self.monitor_service)

    class Admin:
        pass
