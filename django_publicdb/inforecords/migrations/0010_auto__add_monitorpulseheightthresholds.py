# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MonitorPulseheightThresholds'
        db.create_table('inforecords_monitorpulseheightthresholds', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Station'])),
            ('plate', self.gf('django.db.models.fields.IntegerField')()),
            ('mpv_mean', self.gf('django.db.models.fields.FloatField')()),
            ('mpv_sigma', self.gf('django.db.models.fields.FloatField')()),
            ('mpv_max_allowed_drift', self.gf('django.db.models.fields.FloatField')()),
            ('mpv_min_allowed_drift', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('inforecords', ['MonitorPulseheightThresholds'])


    def backwards(self, orm):
        # Deleting model 'MonitorPulseheightThresholds'
        db.delete_table('inforecords_monitorpulseheightthresholds')


    models = {
        'inforecords.cluster': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Cluster'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'clusters'", 'to': "orm['inforecords.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['inforecords.Cluster']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'inforecords.contact': {
            'Meta': {'ordering': "('surname', 'first_name')", 'unique_together': "[('first_name', 'prefix_surname', 'surname')]", 'object_name': 'Contact'},
            'contactinformation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'to': "orm['inforecords.ContactInformation']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefix_surname': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Profession']"}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'inforecords.contactinformation': {
            'Meta': {'ordering': "['city', 'street_1', 'email_work']", 'object_name': 'ContactInformation'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'email_private': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'email_work': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        'inforecords.country': {
            'Meta': {'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'})
        },
        'inforecords.detectorhisparc': {
            'Meta': {'ordering': "('station__number',)", 'object_name': 'DetectorHisparc'},
            'direction': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Station']"}),
            'translation_long': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'translation_perp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'inforecords.electronics': {
            'Meta': {'ordering': "('batch', 'serial')", 'object_name': 'Electronics'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.ElectronicsBatch']"}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'has_gps': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_master': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.IntegerField', [], {}),
            'startdate': ('django.db.models.fields.DateField', [], {}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Station']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.ElectronicsStatus']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.ElectronicsType']"})
        },
        'inforecords.electronicsbatch': {
            'Meta': {'ordering': "('type', 'number')", 'object_name': 'ElectronicsBatch'},
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
            'Meta': {'ordering': "('description',)", 'object_name': 'ElectronicsType'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'inforecords.enabledservice': {
            'Meta': {'ordering': "('pc', 'monitor_service')", 'object_name': 'EnabledService'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'max_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'monitor_service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.MonitorService']"}),
            'pc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Pc']"})
        },
        'inforecords.monitorpulseheightthresholds': {
            'Meta': {'object_name': 'MonitorPulseheightThresholds'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mpv_max_allowed_drift': ('django.db.models.fields.FloatField', [], {}),
            'mpv_mean': ('django.db.models.fields.FloatField', [], {}),
            'mpv_min_allowed_drift': ('django.db.models.fields.FloatField', [], {}),
            'mpv_sigma': ('django.db.models.fields.FloatField', [], {}),
            'plate': ('django.db.models.fields.IntegerField', [], {}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Station']"})
        },
        'inforecords.monitorservice': {
            'Meta': {'ordering': "('description',)", 'object_name': 'MonitorService'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'enable_active_checks': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default_service': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'max_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_critical': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_warning': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'nagios_command': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        'inforecords.pc': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Pc'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_test': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['inforecords.MonitorService']", 'through': "orm['inforecords.EnabledService']", 'symmetrical': 'False'}),
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
            'Meta': {'ordering': "('number',)", 'object_name': 'Station'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['inforecords.Cluster']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations_contact'", 'null': 'True', 'to': "orm['inforecords.Contact']"}),
            'contactinformation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['inforecords.ContactInformation']"}),
            'ict_contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations_ict_contact'", 'null': 'True', 'to': "orm['inforecords.Contact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_page': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }

    complete_apps = ['inforecords']