# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SessionRequest'
        db.create_table('analysissessions_sessionrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sur_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('school', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inforecords.Cluster'])),
            ('events_to_create', self.gf('django.db.models.fields.IntegerField')()),
            ('events_created', self.gf('django.db.models.fields.IntegerField')()),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('mail_send', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('session_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('session_created', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('session_pending', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('sid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('pin', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('analysissessions', ['SessionRequest'])

        # Adding field 'AnalysisSession.pin'
        db.add_column('analysissessions_analysissession', 'pin', self.gf('django.db.models.fields.CharField')(default=0, max_length=4), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'SessionRequest'
        db.delete_table('analysissessions_sessionrequest')

        # Deleting field 'AnalysisSession.pin'
        db.delete_column('analysissessions_analysissession', 'pin')


    models = {
        'analysissessions.analysissession': {
            'Meta': {'object_name': 'AnalysisSession'},
            'ends': ('django.db.models.fields.DateTimeField', [], {}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'starts': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'analysissessions.analyzedcoincidence': {
            'Meta': {'ordering': "('coincidence',)", 'object_name': 'AnalyzedCoincidence'},
            'coincidence': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coincidences.Coincidence']"}),
            'core_position_x': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'core_position_y': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'error_estimate': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_analyzed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'log_energy': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'phi': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysissessions.AnalysisSession']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysissessions.Student']", 'null': 'True', 'blank': 'True'}),
            'theta': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'analysissessions.sessionrequest': {
            'Meta': {'object_name': 'SessionRequest'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Cluster']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'events_created': ('django.db.models.fields.IntegerField', [], {}),
            'events_to_create': ('django.db.models.fields.IntegerField', [], {}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail_send': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pin': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'school': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'session_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session_created': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session_pending': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'sur_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'analysissessions.student': {
            'Meta': {'object_name': 'Student'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysissessions.AnalysisSession']"})
        },
        'coincidences.coincidence': {
            'Meta': {'ordering': "('date', 'time', 'nanoseconds')", 'object_name': 'Coincidence'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'events': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['coincidences.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nanoseconds': ('django.db.models.fields.IntegerField', [], {}),
            'time': ('django.db.models.fields.TimeField', [], {})
        },
        'coincidences.event': {
            'Meta': {'ordering': "('date', 'time', 'nanoseconds', 'station')", 'object_name': 'Event'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'integrals': ('django_publicdb.coincidences.models.SerializedDataField', [], {}),
            'nanoseconds': ('django.db.models.fields.IntegerField', [], {}),
            'pulseheights': ('django_publicdb.coincidences.models.SerializedDataField', [], {}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inforecords.Station']"}),
            'time': ('django.db.models.fields.TimeField', [], {}),
            'traces': ('django_publicdb.coincidences.models.SerializedDataField', [], {})
        },
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
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'})
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

    complete_apps = ['analysissessions']
