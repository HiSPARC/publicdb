from django.contrib.postgres.fields import ArrayField
from django.db import models

from ..inforecords.models import Station


class Coincidence(models.Model):
    date = models.DateField()
    time = models.TimeField()
    nanoseconds = models.IntegerField()

    class Meta:
        verbose_name = 'Coincidence'
        verbose_name_plural = 'Coincidences'
        ordering = ['date', 'time', 'nanoseconds']

    def __str__(self):
        return f'{self.num_events()}-fold - {self.date} {self.time} {self.nanoseconds}'

    def num_events(self):
        return self.events.count()


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

    def __str__(self):
        return f'{self.station.number} - {self.date} {self.time} {self.nanoseconds}'
