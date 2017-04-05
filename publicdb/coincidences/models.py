from django.db import models

import zlib
import cPickle as pickle
import base64
import numpy as np
import json

from ..inforecords.models import Station


class SerializedDataField(models.Field):

    def db_type(self, connection):
        return 'BYTEA'

    # DB/Deserializer -> Python

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):

        # Couple possibilities:

        # 1. If it is a list

        if isinstance(value, list):
            return value

        if not isinstance(value, unicode) and not isinstance(value, str):
            return []

        # 2. If the value is somehow for whatever reason a JSON array formatted
        #    string instead of a JSON array

        if value[0] == '[' and value[-1] == ']':
            return_value = json.loads(value)

            if isinstance(return_value, list):
                return return_value

            return []

        # 3. If the value is a base64 z-compressed pickled python list

        try:
            unpickled = pickle.loads(zlib.decompress(base64.b64decode(value)))
        except pickle.PickleError:
            return eval(value)
        else:
            if isinstance(unpickled, list):
                data = []
                for x in unpickled:
                    if isinstance(x, np.ndarray):
                        data.append(x.tolist())
                    else:
                        data.append(x)
                return data
            else:
                return unpickled

    # Python -> DB

    def get_prep_value(self, value):
        return base64.b64encode(zlib.compress(pickle.dumps(value)))

    # Python -> Serializer

    def value_to_string(self, obj):

        human_readable_output = False

        value = self._get_val_from_obj(obj)

        if human_readable_output:
            return value

        return self.get_prep_value(value)


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
