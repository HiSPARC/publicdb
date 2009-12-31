from django.db import models

import zlib
import cPickle as pickle
import base64

from django_publicdb.inforecords import models as inforecords


class SerializedDataField(models.Field):
    # This makes sure that to_python() will be called when objects are
    # initialized
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(SerializedDataField, self).__init__(*args, **kwargs)

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

class Summary(models.Model):
    station = models.ForeignKey(inforecords.Station)
    date = models.DateField()
    number_of_events = models.IntegerField(blank=True, null=True)
    needs_update = models.BooleanField()

    def __unicode__(self):
        return 'Summary: %d - %s' % (self.station.number,
                                     self.date.strftime('%d %b %Y'))

    class Meta:
        verbose_name_plural = 'summaries'
        unique_together = (('station', 'date'),)
        ordering = ('date', 'station')

class DailyHistogram(models.Model):
    source = models.ForeignKey('Summary')
    type = models.ForeignKey('HistogramType')
    bins = SerializedDataField()
    values = SerializedDataField()

    def __unicode__(self):
        return "%d - %s - %s" % (self.source.station.number,
                                 self.source.date.strftime('%c'), self.type)

    class Meta:
        unique_together = (('source', 'type'),)
        ordering = ('source', 'type')

class HistogramType(models.Model):
    name = models.CharField(max_length=40)
    slug = models.CharField(max_length=20)
    has_multiple_datasets = models.BooleanField()
    bin_axis_title = models.CharField(max_length=40)
    value_axis_title = models.CharField(max_length=40)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

class GeneratorState(models.Model):
    check_last_run = models.DateTimeField()
    check_is_running = models.BooleanField()
    update_last_run = models.DateTimeField()
    update_is_running = models.BooleanField()
