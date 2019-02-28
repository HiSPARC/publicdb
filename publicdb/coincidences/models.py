from django.contrib.postgres.fields import ArrayField
from django.db import models

from ..inforecords.models import Station


class SerializedDataField(models.Field):

    system_check_removed_details = {
        'hint': 'Use ArrayField instead.',
    }

    def db_type(self, connection):
        # Required for old migrations
        return 'BYTEA'


class Coincidence(models.Model):
    date = models.DateField()
    time = models.TimeField()
    nanoseconds = models.IntegerField()

    def num_events(self):
        return self.events.count()

    def __unicode__(self):
        return '%d-fold - %s %s %d' % (self.num_events(), self.date, self.time, self.nanoseconds)

    class Meta:
        verbose_name = 'Coincidence'
        verbose_name_plural = 'Coincidences'
        ordering = ['date', 'time', 'nanoseconds']


class Event(models.Model):
    date = models.DateField()
    time = models.TimeField()
    nanoseconds = models.IntegerField()
    coincidence = models.ForeignKey(Coincidence, models.CASCADE, related_name='events')
    station = models.ForeignKey(Station, models.CASCADE, related_name='events')
    pulseheights = ArrayField(models.IntegerField(), size=4)
    integrals = ArrayField(models.IntegerField(), size=4)
    traces = ArrayField(ArrayField(models.IntegerField()), size=4)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['date', 'time', 'nanoseconds', 'station']

    def __unicode__(self):
        return '%d - %s %s %d' % (self.station.number, self.date, self.time, self.nanoseconds)
