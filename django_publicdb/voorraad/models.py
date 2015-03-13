from django.db import models
from django_publicdb.inforecords.models import *
from django.contrib.auth.models import User
from django_publicdb.middleware import threadlocals
from django.utils.safestring import mark_safe


class Leverancier(models.Model):
    naam = models.CharField(max_length=255)
    adres = models.CharField(max_length=255)
    postcode = models.CharField(max_length=255)
    woonplaats = models.CharField(max_length=255)
    provincie = models.CharField(blank=True, max_length=255)
    land = models.CharField(max_length=255, default='Nederland')
    telefoon = models.CharField(max_length=255)
    fax = models.CharField(blank=True, max_length=255)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    contactpersoon = models.CharField(max_length=255)
    opmerkingen = models.TextField(blank=True)

    # standaard waarde
    def __unicode__(self):
        return self.naam

    class Meta:
        ordering = ['naam']
        verbose_name_plural = 'Leveranciers'


class Opbergplek(models.Model):
    opbergplek = models.CharField(max_length=255, unique=True)

    # standaard waarde
    def __unicode__(self):
        return self.opbergplek

    class Meta:
        ordering = ['opbergplek']
        verbose_name_plural = 'Opbergplekken'


STATUS = (('V', 'V'), ('?', '?'), ('!', '!'), )


class Artikel(models.Model):
    naam = models.CharField(max_length=255)
    opbergplek = models.ForeignKey(Opbergplek)
    aantal = models.IntegerField()
    leverancier = models.ForeignKey(Leverancier)
    artikelnummer = models.CharField(max_length=255)
    datum = models.DateTimeField(auto_now=True)
    opmerkingen = models.TextField(blank=True)
    status = models.CharField(max_length=1, choices=STATUS)

    # standaard waarde
    def __unicode__(self):
        return self.naam

    def commentaar(self):
        if 'V' == self.status:
            kleur = 'v'
        elif '!' == self.status:
            kleur = '<b>!</b>'
        elif '?' == self.status:
            kleur = '<b>?</b>'
        return mark_safe(kleur)

    commentaar.allow_tags = True
    commentaar.short_description = "Status"

    class Meta:
        ordering = ['naam']
        verbose_name_plural = 'Artikelen'


class Apparatuur(models.Model):
    naam = models.CharField(max_length=255)
    opbergplek = models.ForeignKey(Opbergplek)
    aantal = models.IntegerField()
    opmerkingen = models.TextField(blank=True)

    # standaard waarde
    def __unicode__(self):
        return self.naam

    class Meta:
        verbose_name_plural = 'Apparatuur'


class Reservering(models.Model):
    cluster = models.ForeignKey(Cluster)
    aantal = models.IntegerField()
    artikel = models.ForeignKey(Artikel)
    datum = models.DateTimeField(auto_now_add=True)
    voldaan = models.BooleanField(blank=True)
    opmerkingen = models.TextField(blank=True)

    # standaard waarde
    def __unicode__(self):
        return ('%s, %s, %s') % (self.cluster, self.datum, self.artikel)

    class Meta:
        ordering = ['datum', 'artikel']
        verbose_name_plural = 'Reserveringen'


class Gebruikt(models.Model):
    persoon = models.ForeignKey(User)
    artikel = models.ForeignKey(Artikel)
    aantal = models.IntegerField()
    datum = models.DateTimeField(auto_now_add=True)
    cluster = models.ForeignKey(Cluster)
    # reservering = models.ForeignKey(Reservering,blank=True)
    opmerkingen = models.TextField(blank=True)

    # Om de voorraad actueel te houden
    def save(self):
        if self.id:
            oudewaarde = Gebruikt.objects.get(id=self.id).aantal
            self.artikel.aantal = (self.artikel.aantal -
                                   (self.aantal - oudewaarde))
            self.artikel.save()
            super(Gebruikt, self).save()
        else:
            # self.persoon = threadlocals.get_current_user()
            super(Gebruikt, self).save()
            self.artikel.aantal = self.artikel.aantal - self.aantal
            self.artikel.save()

    # standaard waarde
    def __unicode__(self):
        return ('%s, %s') % (self.cluster, self.artikel)

    class Meta:
        ordering = ['datum', 'artikel']
        verbose_name_plural = 'Gebruikt'


class Bestel(models.Model):
    persoon = models.ForeignKey(User, blank=True)
    artikel = models.ForeignKey(Artikel)
    aantalbesteld = models.IntegerField()
    datumbesteld = models.DateTimeField(auto_now_add=True)
    offerte = models.FileField(blank=True, upload_to='offerte')
    levertijd = models.CharField(max_length=255, blank=True)
    aantalgeleverd = models.IntegerField(default='0')
    datumgeleverd = models.DateTimeField(auto_now=True)
    verzendkosten = models.CharField(blank=True, max_length=255)
    voldaan = models.BooleanField(blank=True)
    opmerkingen = models.TextField(blank=True)

    def save(self):
        if self.id:
            oudewaarde = Bestel.objects.get(id=self.id).aantalgeleverd
            self.artikel.aantal = self.artikel.aantal + (self.aantalgeleverd -
                                                         oudewaarde)
            self.artikel.save()
            if self.aantalgeleverd == self.aantalbesteld:
                self.voldaan = True
                super(Bestel, self).save()
            else:
                self.persoon = threadlocals.get_current_user()
                super(Bestel, self).save()

    # standaard waarde
    def __unicode__(self):
        return ('%s %s') % (self.persoon, self.artikel)

    class Meta:
        ordering = ['datumbesteld', 'artikel']
        verbose_name_plural = 'Bestellen'


class HisparcII(models.Model):
    serienummer = models.IntegerField()
    is_master = models.BooleanField(default=True)
    stationnummer = models.IntegerField(blank=True, null=True)
    opstelling = models.CharField(max_length=80, blank=True, null=True)
    plaats = models.CharField(max_length=80, blank=True, null=True)
    status = models.CharField(max_length=80, blank=True, null=True)
    opmerkingen = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'HiSPARC II'
        verbose_name_plural = 'HiSPARC II'
        ordering = ['serienummer']
