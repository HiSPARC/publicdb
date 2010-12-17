# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Profession'
        db.create_table('inforecords_profession', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal('inforecords', ['Profession'])

        # Adding model 'Contact_Information'
        db.create_table('inforecords_contact_information', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street_1', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('street_2', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('postalcode', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('pobox', self.gf('django.db.models.fields.CharField')(max_length=9, null=True, blank=True)),
            ('pobox_postalcode', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('pobox_city', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('phone_work', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('phone_home', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('email_work', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('email_private', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('inforecords', ['Contact_Information'])

        # Adding model 'Country'
        db.create_table('inforecords_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('number', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal('inforecords', ['Country'])

        # Adding field 'Cluster.number'
        db.add_column('inforecords_cluster', 'number', self.gf('django.db.models.fields.IntegerField')(default=0, unique=True, blank=True), keep_default=False)

        # Renaming column for 'Cluster.country' to match new field type.
        db.rename_column('inforecords_cluster', 'country', 'country_id')
        # Changing field 'Cluster.country'
        db.alter_column('inforecords_cluster', 'country_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Country']))

        # Adding index on 'Cluster', fields ['country']
        db.create_index('inforecords_cluster', ['country_id'])

        # Adding field 'Contact.profession'
        db.add_column('inforecords_contact', 'profession', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['inforecords.Profession'], blank=True), keep_default=False)

        # Adding field 'Contact.prefix_surname'
        db.add_column('inforecords_contact', 'prefix_surname', self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True), keep_default=False)

        # Adding field 'Contact.surname'
        db.add_column('inforecords_contact', 'surname', self.gf('django.db.models.fields.CharField')(default='', max_length=40), keep_default=False)

        # Adding field 'Contact.contactinformation'
        db.add_column('inforecords_contact', 'contactinformation', self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='contacts', to=orm['inforecords.Contact_Information']), keep_default=False)

        # Adding field 'Station.name'
        db.add_column('inforecords_station', 'name', self.gf('django.db.models.fields.CharField')(default='', max_length=70), keep_default=False)

        # Adding field 'Station.contact_information'
        db.add_column('inforecords_station', 'contact_information', self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='stations', to=orm['inforecords.Contact_Information']), keep_default=False)

        # Adding field 'Station.ict_contact'
        db.add_column('inforecords_station', 'ict_contact', self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='stations_ict_contact', to=orm['inforecords.Contact']), keep_default=False)

        # Changing field 'Station.number'
        db.alter_column('inforecords_station', 'number', self.gf('django.db.models.fields.IntegerField')(unique=True, blank=True))


    def backwards(self, orm):
        
        # Deleting model 'Profession'
        db.delete_table('inforecords_profession')

        # Deleting model 'Contact_Information'
        db.delete_table('inforecords_contact_information')

        # Deleting model 'Country'
        db.delete_table('inforecords_country')

        # Deleting field 'Cluster.number'
        db.delete_column('inforecords_cluster', 'number')

        # Renaming column for 'Cluster.country' to match new field type.
        db.rename_column('inforecords_cluster', 'country_id', 'country')
        # Changing field 'Cluster.country'
        db.alter_column('inforecords_cluster', 'country', self.gf('django.db.models.fields.CharField')(max_length=40))

        # Removing index on 'Cluster', fields ['country']
        db.delete_index('inforecords_cluster', ['country_id'])

        # Deleting field 'Contact.profession'
        db.delete_column('inforecords_contact', 'profession_id')

        # Deleting field 'Contact.prefix_surname'
        db.delete_column('inforecords_contact', 'prefix_surname')

        # Deleting field 'Contact.surname'
        db.delete_column('inforecords_contact', 'surname')

        # Deleting field 'Contact.contactinformation'
        db.delete_column('inforecords_contact', 'contactinformation_id')

        # Deleting field 'Station.name'
        db.delete_column('inforecords_station', 'name')

        # Deleting field 'Station.contact_information'
        db.delete_column('inforecords_station', 'contact_information_id')

        # Deleting field 'Station.ict_contact'
        db.delete_column('inforecords_station', 'ict_contact_id')

        # Changing field 'Station.number'
        db.alter_column('inforecords_station', 'number', self.gf('django.db.models.fields.IntegerField')(unique=True))


    models = {
        'inforecords.cluster': {
            'Meta': {'object_name': 'Cluster'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Contact']", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'clusters'", 'to': "orm['inforecords.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Cluster']", 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'inforecords.contact': {
            'Meta': {'unique_together': "[('first_name', 'prefix_last_name', 'last_name')]", 'object_name': 'Contact'},
            'contactinformation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'to': "orm['inforecords.Contact_Information']"}),
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
        'inforecords.contact_information': {
            'Meta': {'object_name': 'Contact_Information'},
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
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['inforecords.MonitorService']", 'through': "'EnabledService'", 'symmetrical': 'False'}),
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
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Contact']", 'null': 'True', 'blank': 'True'}),
            'contact_information': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['inforecords.Contact_Information']"}),
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
