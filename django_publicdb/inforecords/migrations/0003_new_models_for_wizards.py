# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Station:
    def __init__(self, number):
        self.number = number

class Migration(DataMigration):

    def forwards(self, orm):
        for obj in orm.Contactposition.objects.all():
            orm.Profession(description=obj.description).save()
        for c in orm.Contact.objects.all():
            c.profession = orm.Profession.objects.get(
                description=c.contactposition.description)
            c.prefix_surname = c.prefix_last_name
            c.surname = c.last_name

            l = c.location
            if l is not None:
                c_info = orm.ContactInformation(
                            street_1=l.address, postalcode=l.postalcode,
                            city=l.city, pobox=l.pobox,
                            pobox_postalcode=l.pobox_postalcode,
                            pobox_city=l.pobox_city, phone_work=c.phone_work,
                            phone_home=c.phone_home, email_work=c.email,
                            url=c.url)
            else:
                c_info = orm.ContactInformation(
                            street_1='', postalcode='', city='',
                            phone_work=c.phone_work,
                            phone_home=c.phone_home, email_work=c.email,
                            url=c.url)
            c_info.save()
            c.contactinformation = c_info
            c.save()
        for s in orm.Station.objects.all():
            s.name = s.location.name
            s.cluster = s.location.cluster
            l = s.location
            c_info = orm.ContactInformation(
                        street_1=l.address, postalcode=l.postalcode,
                        city=l.city, pobox=l.pobox,
                        pobox_postalcode=l.pobox_postalcode,
                        pobox_city=l.pobox_city, phone_work=l.phone,
                        fax=l.fax, email_work=l.email, url=l.url)
            c_info.save()
            s.contact_information = c_info
            s.save()
        for c in orm.Cluster.objects.all():
            if c.name == 'Durham':
                station = Station(12001)
            elif c.name == 'Science Park':
                station = Station(501)
            else:
                station = orm.Station.objects.filter(location__cluster=c)[0]

            country_number = station.number / 10000 * 10000
            cluster_number = station.number / 1000 * 1000
            subcluster_number = station.number / 100 * 100
            if (country_number, cluster_number, subcluster_number) == \
                    (0, 0, 700):
                c.country = 'Netherlands'
                c.parent = orm.Cluster.objects.get(name='Amsterdam')

            if c.parent:
                c.number = subcluster_number
            else:
                c.number = cluster_number

            country, created = orm.Country.objects.get_or_create(
                                name=c.country,
                                number=country_number)
            c.new_country = country
            c.save()

    def backwards(self, orm):
        pass
        #raise NotImplementedError("Backwards migration not implemented.")


    models = {
        'inforecords.cluster': {
            'Meta': {'object_name': 'Cluster'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Contact']", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'}),
            'new_country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'clusters'", 'to': "orm['inforecords.Country']"}),
            'number': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Cluster']", 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'inforecords.contact': {
            'Meta': {'unique_together': "[('first_name', 'prefix_last_name', 'last_name')]", 'object_name': 'Contact'},
            'contactinformation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'to': "orm['inforecords.ContactInformation']"}),
            'contactposition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Contactposition']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contacts'", 'null': 'True', 'to': "orm['inforecords.Location']"}),
            'phone_home': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'phone_work': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'prefix_last_name': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'prefix_surname': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Profession']", 'blank': 'True'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'inforecords.contactinformation': {
            'Meta': {'object_name': 'ContactInformation'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'email_private': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'email_work': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone_home': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'phone_work': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'pobox': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'pobox_city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'pobox_postalcode': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'postalcode': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'street_1': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'street_2': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'inforecords.contactposition': {
            'Meta': {'object_name': 'Contactposition'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'inforecords.country': {
            'Meta': {'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        'inforecords.detectorhisparc': {
            'Meta': {'object_name': 'DetectorHisparc'},
            'direction': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_1_angle': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_1_long': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_1_perp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_2_angle': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_2_long': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_2_perp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_3_angle': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_3_long': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_3_perp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_4_angle': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_4_long': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_4_perp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'startdate': ('django.db.models.fields.DateField', [], {}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Station']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.DetectorStatus']"}),
            'translation_long': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'translation_perp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'inforecords.detectorstatus': {
            'Meta': {'object_name': 'DetectorStatus'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'inforecords.electronics': {
            'Meta': {'object_name': 'Electronics'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.ElectronicsBatch']"}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'has_gps': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_master': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.IntegerField', [], {}),
            'startdate': ('django.db.models.fields.DateField', [], {}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Station']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.ElectronicsStatus']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.ElectronicsType']"})
        },
        'inforecords.electronicsbatch': {
            'Meta': {'object_name': 'ElectronicsBatch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.ElectronicsType']"})
        },
        'inforecords.electronicsstatus': {
            'Meta': {'object_name': 'ElectronicsStatus'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'inforecords.electronicstype': {
            'Meta': {'object_name': 'ElectronicsType'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'inforecords.enabledservice': {
            'Meta': {'object_name': 'EnabledService'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'max_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'monitor_service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.MonitorService']"}),
            'pc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Pc']"})
        },
        'inforecords.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Cluster']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locationstatus': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.LocationStatus']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Organization']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'pobox': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'pobox_city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'pobox_postalcode': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'postalcode': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'inforecords.locationstatus': {
            'Meta': {'object_name': 'LocationStatus'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'inforecords.monitorservice': {
            'Meta': {'object_name': 'MonitorService'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'enable_active_checks': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default_service': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'max_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'max_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'nagios_command': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        'inforecords.organization': {
            'Meta': {'object_name': 'Organization'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'inforecords.pc': {
            'Meta': {'object_name': 'Pc'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['inforecords.MonitorService']", 'through': "'EnabledService'"}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Station']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.PcType']"})
        },
        'inforecords.pctype': {
            'Meta': {'object_name': 'PcType'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'inforecords.profession': {
            'Meta': {'object_name': 'Profession'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'inforecords.station': {
            'Meta': {'object_name': 'Station'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['inforecords.Cluster']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Contact']", 'null': 'True', 'blank': 'True'}),
            'contact_information': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['inforecords.ContactInformation']"}),
            'ict_contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations_ict_contact'", 'to': "orm['inforecords.Contact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_page': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }

    complete_apps = ['inforecords']
