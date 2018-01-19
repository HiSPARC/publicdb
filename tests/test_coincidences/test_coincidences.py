from django.core import serializers
from django.test import TestCase

from publicdb.inforecords.models import *
from publicdb.coincidences.models import *


class SerializationTestCase(TestCase):

    fixtures = ['tests_inforecords']

    def test_event_serialization_json(self):

        # Create an event and save it to the database

        station = Station.objects.all()[0]
        event = Event(date="2010-05-01",
                      time="00:09:15",
                      nanoseconds=665162853,
                      station=station,
                      pulseheights=[1, 2, 3, 4],
                      integrals=[1, 2, 3, 4],
                      traces=[[1, 2, 3, 4], [1, 2, 3, 4]])
        event.save()

        self.assertEqual(len(Event.objects.all()), 1)

        # Retrieve the first event and serialize it

        original_event = Event.objects.all()[0]
        serialized_event = serializers.serialize("json", [original_event])

        # Deserialize the event

        iterator = serializers.deserialize("json", serialized_event)
        deserialized_event = iterator.next().object

        self.assertEqual(original_event, deserialized_event)

    def test_event_serialization_xml(self):

        # Create an event and save it to the database

        station = Station.objects.all()[0]

        event = Event(date="2010-05-01",
                      time="00:09:15",
                      nanoseconds=665162853,
                      station=station,
                      pulseheights=[1, 2, 3, 4],
                      integrals=[1, 2, 3, 4],
                      traces=[[1, 2, 3, 4], [1, 2, 3, 4]])
        event.save()

        self.assertEqual(len(Event.objects.all()), 1)

        # Retrieve the first event and serialize it

        original_event = Event.objects.all()[0]
        serialized_event = serializers.serialize("xml", [original_event])

        # Deserialize the event

        iterator = serializers.deserialize("xml", serialized_event)
        deserialized_event = iterator.next().object

        self.assertEqual(original_event, deserialized_event)
