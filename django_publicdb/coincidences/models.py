from django.db import models
import zlib
import cPickle as pickle
import base64


class TraceField(models.Field):
    # This makes sure that to_python() will be called when objects are
    # initialized
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(TraceField, self).__init__(*args, **kwargs)

    def db_type(self):
        return 'LONGBLOB'

    def to_python(self, value):
        try:
            unpickled = pickle.loads(zlib.decompress(base64.b64decode(value)))
        except:
            return value
        else:
            return unpickled

    def get_db_prep_value(self, value):
        return base64.b64encode(zlib.compress(pickle.dumps(value)))


class Coincidence(models.Model):
    date = models.DateField()
    time = models.TimeField(null=True)
    nanoseconds = models.IntegerField(null=True)
    timestamp = models.FloatField('nanoseconds from midnight', null=True)
    events = models.ManyToManyField('Event', null=True, default=None)
    nevents = models.IntegerField('Number of events', default=0)
    nodouble = models.BooleanField('No detectors double?', default=True)
    intime = models.BooleanField('x < c*dt?', default=True)
    
    def event_ids(self):
        return self.events.values_list('event_id')

    def __unicode__(self):
        return str(self.id)
    
    class Meta:
        ordering = ('date',)

    
class Event(models.Model):
    event_id = models.IntegerField('Event id from event warehouse', primary_key=True)
    date = models.DateField()
    time = models.TimeField()
    nanoseconds = models.IntegerField()
    timestamp = models.FloatField('nanoseconds from midnight')
    detector = models.IntegerField('Detector number')
    latitude = models.FloatField()
    longitude = models.FloatField()
    height = models.FloatField()
    pulseheight1 = models.FloatField()
    pulseheight2 = models.FloatField()
    pulseheight3 = models.FloatField()
    pulseheight4 = models.FloatField()
    integral1 = models.FloatField()
    integral2 = models.FloatField()
    integral3 = models.FloatField()
    integral4 = models.FloatField()
    trace1 = TraceField()
    trace2 = TraceField()
    trace3 = TraceField()
    trace4 = TraceField()
    
    def __unicode__(self):
        return str(self.event_id)
    
    class Meta:
        ordering = ('date',)
