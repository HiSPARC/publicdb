from django.test import TestCase
from django.core import serializers

from django_publicdb.coincidences.models import *
from django_publicdb.inforecords.models import *

class MyCoincidencesTests(TestCase):

    fixtures = [
        'tests_inforecords'
    ]

    #---------------------------------------------------------------------------
    # Setup and teardown
    #---------------------------------------------------------------------------

    def setUp(self):
        super(MyCoincidencesTests, self).setUp()

    def tearDown(self):
        super(MyCoincidencesTests, self).tearDown()

    #---------------------------------------------------------------------------
    # Tests
    #---------------------------------------------------------------------------

    def test_Event_Serialization_JSON(self):

        # Create an event and save it to the database

        station = Station.objects.all()[0]

        event = Event(
            date = "2010-05-01",
            time = "00:09:15",
            nanoseconds = 665162853,
            station = station,
            pulseheights = [1, 2, 3, 4],
            integrals = [1, 2, 3, 4],
            traces = [[1, 2, 3, 4]]
        )

        event.save()

        assert len(Event.objects.all()) == 1

        # Retrieve the first event and serialize it

        original_event = Event.objects.all()[0]

        serialized_event = serializers.serialize("json", [original_event])

        # Deserialize the event

        iterator = serializers.deserialize("json", serialized_event)

        deserialized_event = iterator.next().object

        self.assertEqual(original_event, deserialized_event)

    def test_Event_Serialization_XML(self):

        # Create an event and save it to the database

        station = Station.objects.all()[0]

        event = Event(
            date = "2010-05-01",
            time = "00:09:15",
            nanoseconds = 665162853,
            station = station,
            pulseheights = [1, 2, 3, 4],
            integrals = [1, 2, 3, 4],
            traces = [[1, 2, 3, 4]]
        )

        event.save()

        assert len(Event.objects.all()) == 1

        # Retrieve the first event and serialize it

        original_event = Event.objects.all()[0]

        serialized_event = serializers.serialize("xml", [original_event])

        # Deserialize the event

        iterator = serializers.deserialize("xml", serialized_event)

        deserialized_event = iterator.next().object

        self.assertEqual(original_event, deserialized_event)

