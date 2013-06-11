# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Deleting model 'DetectorStatus'
        db.delete_table('inforecords_detectorstatus')

        # Deleting model 'Location'
        db.delete_table('inforecords_location')

        # Deleting model 'LocationStatus'
        db.delete_table('inforecords_locationstatus')

        # Deleting model 'Organization'
        db.delete_table('inforecords_organization')

        # Deleting model 'Contactposition'
        db.delete_table('inforecords_contactposition')

        # Deleting field 'DetectorHisparc.status'
        db.delete_column('inforecords_detectorhisparc', 'status_id')

        # Deleting field 'Cluster.country'
        db.delete_column('inforecords_cluster', 'country')

        # Deleting field 'Cluster.contact'
        db.delete_column('inforecords_cluster', 'contact_id')

        # Adding unique constraint on 'Cluster', fields ['number']
        db.create_unique('inforecords_cluster', ['number'])

        # Removing unique constraint on 'Contact', fields ['first_name', 'last_name', 'prefix_last_name']
        db.delete_unique('inforecords_contact', ['first_name', 'last_name', 'prefix_last_name'])

        # Deleting field 'Contact.last_name'
        db.delete_column('inforecords_contact', 'last_name')

        # Deleting field 'Contact.phone_work'
        db.delete_column('inforecords_contact', 'phone_work')

        # Deleting field 'Contact.prefix_last_name'
        db.delete_column('inforecords_contact', 'prefix_last_name')

        # Deleting field 'Contact.url'
        db.delete_column('inforecords_contact', 'url')

        # Deleting field 'Contact.contactposition'
        db.delete_column('inforecords_contact', 'contactposition_id')

        # Deleting field 'Contact.phone_home'
        db.delete_column('inforecords_contact', 'phone_home')

        # Deleting field 'Contact.location'
        db.delete_column('inforecords_contact', 'location_id')

        # Deleting field 'Contact.email'
        db.delete_column('inforecords_contact', 'email')

        # Changing field 'Contact.profession'
        db.alter_column('inforecords_contact', 'profession_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Profession']))

        # Adding unique constraint on 'Contact', fields ['prefix_surname', 'first_name', 'surname']
        db.create_unique('inforecords_contact', ['prefix_surname', 'first_name', 'surname'])

        # Deleting field 'Station.location'
        db.delete_column('inforecords_station', 'location_id')

        # Changing field 'Station.contact'
        db.alter_column('inforecords_station', 'contact_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['inforecords.Contact']))

        # Changing field 'Station.ict_contact'
        db.alter_column('inforecords_station', 'ict_contact_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['inforecords.Contact']))


    def backwards(self, orm):

        # Adding model 'DetectorStatus'
        db.create_table('inforecords_detectorstatus', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=40, unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('inforecords', ['DetectorStatus'])

        # Adding model 'Location'
        db.create_table('inforecords_location', (
            ('city', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('pobox_postalcode', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=70, unique=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('pobox', self.gf('django.db.models.fields.CharField')(max_length=9, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Cluster'])),
            ('locationstatus', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.LocationStatus'])),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('postalcode', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Organization'])),
            ('pobox_city', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
        ))
        db.send_create_signal('inforecords', ['Location'])

        # Adding model 'LocationStatus'
        db.create_table('inforecords_locationstatus', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=40, unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('inforecords', ['LocationStatus'])

        # Adding model 'Organization'
        db.create_table('inforecords_organization', (
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40, unique=True)),
        ))
        db.send_create_signal('inforecords', ['Organization'])

        # Adding model 'Contactposition'
        db.create_table('inforecords_contactposition', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=40, unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('inforecords', ['Contactposition'])

        # Adding field 'DetectorHisparc.status'
        db.add_column('inforecords_detectorhisparc', 'status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.DetectorStatus']), keep_default=False)

        # Adding field 'Cluster.country'
        db.add_column('inforecords_cluster', 'country', self.gf('django.db.models.fields.CharField')(default='', max_length=40), keep_default=False)

        # Adding field 'Cluster.contact'
        db.add_column('inforecords_cluster', 'contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Contact'], null=True, blank=True), keep_default=False)

        # Removing unique constraint on 'Cluster', fields ['number']
        db.delete_unique('inforecords_cluster', ['number'])

        # Adding field 'Contact.last_name'
        db.add_column('inforecords_contact', 'last_name', self.gf('django.db.models.fields.CharField')(default='', max_length=40), keep_default=False)

        # Adding field 'Contact.phone_work'
        db.add_column('inforecords_contact', 'phone_work', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True), keep_default=False)

        # Adding field 'Contact.prefix_last_name'
        db.add_column('inforecords_contact', 'prefix_last_name', self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True), keep_default=False)

        # Adding field 'Contact.url'
        db.add_column('inforecords_contact', 'url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True), keep_default=False)

        # Adding field 'Contact.contactposition'
        db.add_column('inforecords_contact', 'contactposition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Contactposition']), keep_default=False)

        # Adding field 'Contact.phone_home'
        db.add_column('inforecords_contact', 'phone_home', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True), keep_default=False)

        # Adding field 'Contact.location'
        db.add_column('inforecords_contact', 'location', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contacts', null=True, to=orm['inforecords.Location'], blank=True), keep_default=False)

        # Adding field 'Contact.email'
        db.add_column('inforecords_contact', 'email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True), keep_default=False)

        # Changing field 'Contact.profession'
        db.alter_column('inforecords_contact', 'profession_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Profession'], blank=True))

        # Adding unique constraint on 'Contact', fields ['first_name', 'last_name', 'prefix_last_name']
        db.create_unique('inforecords_contact', ['first_name', 'last_name', 'prefix_last_name'])

        # Removing unique constraint on 'Contact', fields ['prefix_surname', 'first_name', 'surname']
        db.delete_unique('inforecords_contact', ['prefix_surname', 'first_name', 'surname'])

        # Adding field 'Station.location'
        db.add_column('inforecords_station', 'location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Location']), keep_default=False)

        # Changing field 'Station.contact'
        db.alter_column('inforecords_station', 'contact_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Contact'], null=True, blank=True))

        # Changing field 'Station.ict_contact'
        db.alter_column('inforecords_station', 'ict_contact_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Contact']))


    models = {
        'inforecords.cluster': {
            'Meta': {'object_name': 'Cluster'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'}),
            'new_country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'clusters'", 'to': "orm['inforecords.Country']"}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['inforecords.Cluster']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'inforecords.contact': {
            'Meta': {'unique_together': "[('first_name', 'prefix_surname', 'surname')]", 'object_name': 'Contact'},
            'contactinformation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'to': "orm['inforecords.ContactInformation']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefix_surname': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Profession']"}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
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
            'translation_long': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'translation_perp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
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
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations_contact'", 'null': 'True', 'to': "orm['inforecords.Contact']"}),
            'contact_information': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['inforecords.ContactInformation']"}),
            'ict_contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations_ict_contact'", 'null': 'True', 'to': "orm['inforecords.Contact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_page': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }

    complete_apps = ['inforecords']
