# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Profession'
        db.create_table(u'inforecords_profession', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal(u'inforecords', ['Profession'])

        # Adding model 'Contact'
        db.create_table(u'inforecords_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profession', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Profession'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('prefix_surname', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('contactinformation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contacts', to=orm['inforecords.ContactInformation'])),
        ))
        db.send_create_signal(u'inforecords', ['Contact'])

        # Adding unique constraint on 'Contact', fields ['first_name', 'prefix_surname', 'surname']
        db.create_unique(u'inforecords_contact', ['first_name', 'prefix_surname', 'surname'])

        # Adding model 'ContactInformation'
        db.create_table(u'inforecords_contactinformation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street_1', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('street_2', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('postalcode', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('pobox', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('pobox_postalcode', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('pobox_city', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('phone_work', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('phone_home', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('email_work', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('email_private', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'inforecords', ['ContactInformation'])

        # Adding model 'Cluster'
        db.create_table(u'inforecords_cluster', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=70)),
            ('number', self.gf('django.db.models.fields.IntegerField')(unique=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['inforecords.Cluster'])),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(related_name='clusters', to=orm['inforecords.Country'])),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'inforecords', ['Cluster'])

        # Adding model 'Station'
        db.create_table(u'inforecords_station', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('number', self.gf('django.db.models.fields.IntegerField')(unique=True, blank=True)),
            ('contactinformation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stations', to=orm['inforecords.ContactInformation'])),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stations', to=orm['inforecords.Cluster'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stations_contact', null=True, to=orm['inforecords.Contact'])),
            ('ict_contact', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stations_ict_contact', null=True, to=orm['inforecords.Contact'])),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('info_page', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'inforecords', ['Station'])

        # Adding model 'Country'
        db.create_table(u'inforecords_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('number', self.gf('django.db.models.fields.IntegerField')(unique=True, blank=True)),
        ))
        db.send_create_signal(u'inforecords', ['Country'])

        # Adding model 'DetectorHisparc'
        db.create_table(u'inforecords_detectorhisparc', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Station'])),
            ('startdate', self.gf('django.db.models.fields.DateField')()),
            ('enddate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('direction', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('translation_perp', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('translation_long', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_1_alpha', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_1_beta', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_1_radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_1_height', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_2_alpha', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_2_beta', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_2_radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_2_height', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_3_alpha', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_3_beta', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_3_radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_3_height', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_4_alpha', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_4_beta', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_4_radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_4_height', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inforecords', ['DetectorHisparc'])

        # Adding model 'ElectronicsType'
        db.create_table(u'inforecords_electronicstype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal(u'inforecords', ['ElectronicsType'])

        # Adding model 'ElectronicsStatus'
        db.create_table(u'inforecords_electronicsstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal(u'inforecords', ['ElectronicsStatus'])

        # Adding model 'ElectronicsBatch'
        db.create_table(u'inforecords_electronicsbatch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.ElectronicsType'])),
            ('number', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('notes', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'inforecords', ['ElectronicsBatch'])

        # Adding model 'Electronics'
        db.create_table(u'inforecords_electronics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Station'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.ElectronicsType'])),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.ElectronicsStatus'])),
            ('startdate', self.gf('django.db.models.fields.DateField')()),
            ('enddate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('batch', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.ElectronicsBatch'])),
            ('serial', self.gf('django.db.models.fields.IntegerField')()),
            ('is_master', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_gps', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inforecords', ['Electronics'])

        # Adding model 'PcType'
        db.create_table(u'inforecords_pctype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'inforecords', ['PcType'])

        # Adding model 'Pc'
        db.create_table(u'inforecords_pc', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Station'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.PcType'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_test', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(unique=True, max_length=15, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'inforecords', ['Pc'])

        # Adding model 'MonitorPulseheightThresholds'
        db.create_table(u'inforecords_monitorpulseheightthresholds', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Station'])),
            ('plate', self.gf('django.db.models.fields.IntegerField')()),
            ('mpv_mean', self.gf('django.db.models.fields.FloatField')()),
            ('mpv_sigma', self.gf('django.db.models.fields.FloatField')()),
            ('mpv_max_allowed_drift', self.gf('django.db.models.fields.FloatField')()),
            ('mpv_min_allowed_drift', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'inforecords', ['MonitorPulseheightThresholds'])

        # Adding model 'MonitorService'
        db.create_table(u'inforecords_monitorservice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('nagios_command', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('is_default_service', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('enable_active_checks', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('min_critical', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('max_critical', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('min_warning', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('max_warning', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inforecords', ['MonitorService'])

        # Adding model 'EnabledService'
        db.create_table(u'inforecords_enabledservice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Pc'])),
            ('monitor_service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.MonitorService'])),
            ('min_critical', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('max_critical', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('min_warning', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('max_warning', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inforecords', ['EnabledService'])

        # Adding model 'Quarantine'
        db.create_table(u'inforecords_quarantine', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sur_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Station'])),
            ('detectors', self.gf('django.db.models.fields.IntegerField')()),
            ('active_date', self.gf('django.db.models.fields.DateField')()),
            ('submit_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('hash_applicant', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('hash_reviewer', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('scintillator_1_alpha', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_1_beta', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_1_radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_1_height', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_2_alpha', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_2_beta', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_2_radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_2_height', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_3_alpha', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_3_beta', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_3_radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_3_height', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_4_alpha', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_4_beta', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_4_radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('scintillator_4_height', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'inforecords', ['Quarantine'])


    def backwards(self, orm):
        # Removing unique constraint on 'Contact', fields ['first_name', 'prefix_surname', 'surname']
        db.delete_unique(u'inforecords_contact', ['first_name', 'prefix_surname', 'surname'])

        # Deleting model 'Profession'
        db.delete_table(u'inforecords_profession')

        # Deleting model 'Contact'
        db.delete_table(u'inforecords_contact')

        # Deleting model 'ContactInformation'
        db.delete_table(u'inforecords_contactinformation')

        # Deleting model 'Cluster'
        db.delete_table(u'inforecords_cluster')

        # Deleting model 'Station'
        db.delete_table(u'inforecords_station')

        # Deleting model 'Country'
        db.delete_table(u'inforecords_country')

        # Deleting model 'DetectorHisparc'
        db.delete_table(u'inforecords_detectorhisparc')

        # Deleting model 'ElectronicsType'
        db.delete_table(u'inforecords_electronicstype')

        # Deleting model 'ElectronicsStatus'
        db.delete_table(u'inforecords_electronicsstatus')

        # Deleting model 'ElectronicsBatch'
        db.delete_table(u'inforecords_electronicsbatch')

        # Deleting model 'Electronics'
        db.delete_table(u'inforecords_electronics')

        # Deleting model 'PcType'
        db.delete_table(u'inforecords_pctype')

        # Deleting model 'Pc'
        db.delete_table(u'inforecords_pc')

        # Deleting model 'MonitorPulseheightThresholds'
        db.delete_table(u'inforecords_monitorpulseheightthresholds')

        # Deleting model 'MonitorService'
        db.delete_table(u'inforecords_monitorservice')

        # Deleting model 'EnabledService'
        db.delete_table(u'inforecords_enabledservice')

        # Deleting model 'Quarantine'
        db.delete_table(u'inforecords_quarantine')


    models = {
        u'inforecords.cluster': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Cluster'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'clusters'", 'to': u"orm['inforecords.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['inforecords.Cluster']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'inforecords.contact': {
            'Meta': {'ordering': "('surname', 'first_name')", 'unique_together': "[('first_name', 'prefix_surname', 'surname')]", 'object_name': 'Contact'},
            'contactinformation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'to': u"orm['inforecords.ContactInformation']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefix_surname': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.Profession']"}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'inforecords.contactinformation': {
            'Meta': {'ordering': "['city', 'street_1', 'email_work']", 'object_name': 'ContactInformation'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'email_private': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'email_work': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone_home': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'phone_work': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'pobox': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'pobox_city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'pobox_postalcode': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'postalcode': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'street_1': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'street_2': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'inforecords.country': {
            'Meta': {'object_name': 'Country'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'})
        },
        u'inforecords.detectorhisparc': {
            'Meta': {'ordering': "('station__number',)", 'object_name': 'DetectorHisparc'},
            'direction': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_1_alpha': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_1_beta': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_1_height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_1_radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_2_alpha': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_2_beta': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_2_height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_2_radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_3_alpha': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_3_beta': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_3_height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_3_radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_4_alpha': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_4_beta': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_4_height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_4_radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'startdate': ('django.db.models.fields.DateField', [], {}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.Station']"}),
            'translation_long': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'translation_perp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'inforecords.electronics': {
            'Meta': {'ordering': "('batch', 'serial')", 'object_name': 'Electronics'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.ElectronicsBatch']"}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'has_gps': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_master': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.IntegerField', [], {}),
            'startdate': ('django.db.models.fields.DateField', [], {}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.Station']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.ElectronicsStatus']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.ElectronicsType']"})
        },
        u'inforecords.electronicsbatch': {
            'Meta': {'ordering': "('type', 'number')", 'object_name': 'ElectronicsBatch'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.ElectronicsType']"})
        },
        u'inforecords.electronicsstatus': {
            'Meta': {'object_name': 'ElectronicsStatus'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'inforecords.electronicstype': {
            'Meta': {'ordering': "('description',)", 'object_name': 'ElectronicsType'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'inforecords.enabledservice': {
            'Meta': {'ordering': "('pc', 'monitor_service')", 'object_name': 'EnabledService'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'max_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'monitor_service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.MonitorService']"}),
            'pc': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.Pc']"})
        },
        u'inforecords.monitorpulseheightthresholds': {
            'Meta': {'object_name': 'MonitorPulseheightThresholds'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mpv_max_allowed_drift': ('django.db.models.fields.FloatField', [], {}),
            'mpv_mean': ('django.db.models.fields.FloatField', [], {}),
            'mpv_min_allowed_drift': ('django.db.models.fields.FloatField', [], {}),
            'mpv_sigma': ('django.db.models.fields.FloatField', [], {}),
            'plate': ('django.db.models.fields.IntegerField', [], {}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.Station']"})
        },
        u'inforecords.monitorservice': {
            'Meta': {'ordering': "('description',)", 'object_name': 'MonitorService'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'enable_active_checks': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default_service': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'max_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'nagios_command': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        u'inforecords.pc': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Pc'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_test': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['inforecords.MonitorService']", 'through': u"orm['inforecords.EnabledService']", 'symmetrical': 'False'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.Station']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.PcType']"})
        },
        u'inforecords.pctype': {
            'Meta': {'object_name': 'PcType'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'inforecords.profession': {
            'Meta': {'object_name': 'Profession'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'inforecords.quarantine': {
            'Meta': {'object_name': 'Quarantine'},
            'active_date': ('django.db.models.fields.DateField', [], {}),
            'detectors': ('django.db.models.fields.IntegerField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'hash_applicant': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'hash_reviewer': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scintillator_1_alpha': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_1_beta': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_1_height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_1_radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_2_alpha': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_2_beta': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_2_height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_2_radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_3_alpha': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_3_beta': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_3_height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_3_radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_4_alpha': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_4_beta': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_4_height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'scintillator_4_radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inforecords.Station']"}),
            'submit_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'sur_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'inforecords.station': {
            'Meta': {'ordering': "('number',)", 'object_name': 'Station'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': u"orm['inforecords.Cluster']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations_contact'", 'null': 'True', 'to': u"orm['inforecords.Contact']"}),
            'contactinformation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': u"orm['inforecords.ContactInformation']"}),
            'ict_contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations_ict_contact'", 'null': 'True', 'to': u"orm['inforecords.Contact']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_page': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }

    complete_apps = ['inforecords']