from django.db import models
from hisparc.inforecords.models import *

class EventType(models.Model):
    description = models.CharField(max_length=40)
    electronicstype = models.ForeignKey('inforecords.ElectronicsType')

    def __str__(self):
        return '%s: %s' % (self.electronicstype, self.description)
    
    class Admin:
        pass


class Event(models.Model):
    datetime = models.DateTimeField()
    nanoseconds = models.PositiveIntegerField(max_length=9)
    event_type = models.ForeignKey(EventType)
    station = models.ForeignKey('inforecords.Station')

    class Admin:
        list_display = ('datetime', 'nanoseconds', 'event_type',
                        'station')
