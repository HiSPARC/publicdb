import base64
import cPickle as pickle
import zlib

from django.db import models

from ..inforecords.models import Station


class SerializedDataField(models.Field):

    def db_type(self, connection):
        return 'BYTEA'

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        try:
            unpickled = pickle.loads(zlib.decompress(base64.b64decode(value)))
        except Exception:
            return value
        else:
            return unpickled

    def get_prep_value(self, value):
        return base64.b64encode(zlib.compress(pickle.dumps(value)))


class Event(models.Model):
    date = models.DateField()
    time = models.TimeField()
    nanoseconds = models.IntegerField()
    station = models.ForeignKey(Station, models.CASCADE)
    pulseheights = SerializedDataField()
    integrals = SerializedDataField()
    traces = SerializedDataField()

    class Meta:
        ordering = ('date', 'time', 'nanoseconds', 'station')

    def __unicode__(self):
        return '%d - %s %s %d' % (self.station.number, self.date, self.time,
                                  self.nanoseconds)


class Coincidence(models.Model):
    date = models.DateField()
    time = models.TimeField()
    nanoseconds = models.IntegerField()
    events = models.ManyToManyField(Event)

    def num_events(self):
        return self.events.count()

    def __unicode__(self):
        return '%d-fold - %s %s %d' % (self.num_events(), self.date,
                                       self.time, self.nanoseconds)

    class Meta:
        ordering = ('date', 'time', 'nanoseconds')
