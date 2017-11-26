from django.db import models

from ..inforecords.models import Station
from ..histograms.models import SerializedDataField


class Event(models.Model):
    date = models.DateField()
    time = models.TimeField()
    nanoseconds = models.IntegerField()
    station = models.ForeignKey(Station)
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
