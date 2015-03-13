from django.db import models

import zlib
import cPickle as pickle
import base64
import numpy as np
import json

from django_publicdb.inforecords import models as inforecords
from south.modelsinspector import add_introspection_rules


class SerializedDataField(models.Field):
    # This makes sure that to_python() will be called when objects are
    # initialized
    __metaclass__ = models.SubfieldBase
    add_introspection_rules([], ["^django_publicdb\.coincidences\.models\.SerializedDataField"])

    def db_type(self, connection):
        return 'LONGBLOB'

    # DB/Deserializer -> Python

    def to_python(self, value):

        # Couple possibilities:
        #
        # 1. It is already a list
        # 2. It is a JSON array formatted string
        # 3. It is a base64 encoded zlib compressed pickle string

        # 1. If it is a list

        if isinstance(value, list):
            return value

        if not isinstance(value, unicode) and not isinstance(value, str):
            return []

        # 2. If the value is somehow for whatever reason a JSON array formatted
        #    string instead of a JSON array

        if value[0] == '[' and value[-1] == ']':
            returnValue = json.loads(value)

            if isinstance(returnValue, list):
                return returnValue

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

        HUMAN_READABLE_OUTPUT = False

        value = self._get_val_from_obj(obj)

        if HUMAN_READABLE_OUTPUT:
            return value

        return self.get_prep_value(value)


class Event(models.Model):
    date = models.DateField()
    time = models.TimeField()
    nanoseconds = models.IntegerField()
    station = models.ForeignKey(inforecords.Station)
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
