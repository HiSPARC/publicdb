# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Contactposition'
        db.create_table('inforecords_contactposition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal('inforecords', ['Contactposition'])

        # Adding model 'Contact'
        db.create_table('inforecords_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='contacts', null=True, to=orm['inforecords.Location'])),
            ('contactposition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Contactposition'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('prefix_last_name', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('phone_work', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('phone_home', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal('inforecords', ['Contact'])

        # Adding unique constraint on 'Contact', fields ['first_name', 'prefix_last_name', 'last_name']
        db.create_unique('inforecords_contact', ['first_name', 'prefix_last_name', 'last_name'])

        # Adding model 'Organization'
        db.create_table('inforecords_organization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('inforecords', ['Organization'])

        # Adding model 'Cluster'
        db.create_table('inforecords_cluster', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=70)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Cluster'], null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Contact'], null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('inforecords', ['Cluster'])

        # Adding model 'LocationStatus'
        db.create_table('inforecords_locationstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal('inforecords', ['LocationStatus'])

        # Adding model 'Location'
        db.create_table('inforecords_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=70)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Organization'])),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Cluster'])),
            ('locationstatus', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.LocationStatus'])),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('postalcode', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('pobox', self.gf('django.db.models.fields.CharField')(max_length=9, null=True, blank=True)),
            ('pobox_postalcode', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('pobox_city', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
        ))
        db.send_create_signal('inforecords', ['Location'])

        # Adding model 'Station'
        db.create_table('inforecords_station', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Location'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Contact'], null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('info_page', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('inforecords', ['Station'])

        # Adding model 'DetectorStatus'
        db.create_table('inforecords_detectorstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal('inforecords', ['DetectorStatus'])

        # Adding model 'DetectorHisparc'
        db.create_table('inforecords_detectorhisparc', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Station'])),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.DetectorStatus'])),
            ('startdate', self.gf('django.db.models.fields.DateField')()),
            ('enddate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('direction', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('translation_perp', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('translation_long', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_1_perp', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_1_long', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_1_angle', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_2_perp', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_2_long', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_2_angle', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_3_perp', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_3_long', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_3_angle', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_4_perp', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_4_long', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_4_angle', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('inforecords', ['DetectorHisparc'])

        # Adding model 'ElectronicsType'
        db.create_table('inforecords_electronicstype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal('inforecords', ['ElectronicsType'])

        # Adding model 'ElectronicsStatus'
        db.create_table('inforecords_electronicsstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal('inforecords', ['ElectronicsStatus'])

        # Adding model 'ElectronicsBatch'
        db.create_table('inforecords_electronicsbatch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.ElectronicsType'])),
            ('number', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('notes', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('inforecords', ['ElectronicsBatch'])

        # Adding model 'Electronics'
        db.create_table('inforecords_electronics', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Station'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.ElectronicsType'])),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.ElectronicsStatus'])),
            ('startdate', self.gf('django.db.models.fields.DateField')()),
            ('enddate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('batch', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.ElectronicsBatch'])),
            ('serial', self.gf('django.db.models.fields.IntegerField')()),
            ('is_master', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('has_gps', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('inforecords', ['Electronics'])

        # Adding model 'PcType'
        db.create_table('inforecords_pctype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('inforecords', ['PcType'])

        # Adding model 'Pc'
        db.create_table('inforecords_pc', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Station'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.PcType'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(unique=True, max_length=15, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('inforecords', ['Pc'])

        # Adding model 'MonitorService'
        db.create_table('inforecords_monitorservice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('nagios_command', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('is_default_service', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('enable_active_checks', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('min_critical', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('max_critical', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('min_warning', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('max_warning', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('inforecords', ['MonitorService'])

        # Adding model 'EnabledService'
        db.create_table('inforecords_enabledservice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Pc'])),
            ('monitor_service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.MonitorService'])),
            ('min_critical', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('max_critical', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('min_warning', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('max_warning', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('inforecords', ['EnabledService'])


    def backwards(self, orm):
        
        # Deleting model 'Contactposition'
        db.delete_table('inforecords_contactposition')

        # Deleting model 'Contact'
        db.delete_table('inforecords_contact')

        # Removing unique constraint on 'Contact', fields ['first_name', 'prefix_last_name', 'last_name']
        db.delete_unique('inforecords_contact', ['first_name', 'prefix_last_name', 'last_name'])

        # Deleting model 'Organization'
        db.delete_table('inforecords_organization')

        # Deleting model 'Cluster'
        db.delete_table('inforecords_cluster')

        # Deleting model 'LocationStatus'
        db.delete_table('inforecords_locationstatus')

        # Deleting model 'Location'
        db.delete_table('inforecords_location')

        # Deleting model 'Station'
        db.delete_table('inforecords_station')

        # Deleting model 'DetectorStatus'
        db.delete_table('inforecords_detectorstatus')

        # Deleting model 'DetectorHisparc'
        db.delete_table('inforecords_detectorhisparc')

        # Deleting model 'ElectronicsType'
        db.delete_table('inforecords_electronicstype')

        # Deleting model 'ElectronicsStatus'
        db.delete_table('inforecords_electronicsstatus')

        # Deleting model 'ElectronicsBatch'
        db.delete_table('inforecords_electronicsbatch')

        # Deleting model 'Electronics'
        db.delete_table('inforecords_electronics')

        # Deleting model 'PcType'
        db.delete_table('inforecords_pctype')

        # Deleting model 'Pc'
        db.delete_table('inforecords_pc')

        # Deleting model 'MonitorService'
        db.delete_table('inforecords_monitorservice')

        # Deleting model 'EnabledService'
        db.delete_table('inforecords_enabledservice')


    models = {
        'inforecords.cluster': {
            'Meta': {'object_name': 'Cluster'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Contact']", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Cluster']", 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'inforecords.contact': {
            'Meta': {'unique_together': "[('first_name', 'prefix_last_name', 'last_name')]", 'object_name': 'Contact'},
            'contactposition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Contactposition']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contacts'", 'null': 'True', 'to': "orm['inforecords.Location']"}),
            'phone_home': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'phone_work': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'prefix_last_name': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'inforecords.contactposition': {
            'Meta': {'object_name': 'Contactposition'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        'inforecords.station': {
            'Meta': {'object_name': 'Station'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Contact']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_page': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Location']"}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }

    complete_apps = ['inforecords']
