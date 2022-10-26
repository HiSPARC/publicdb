import datetime
import time

from os.path import dirname, join

from django.conf import settings
from django.test import TestCase, override_settings

from publicdb.histograms import datastore


@override_settings(DATASTORE_PATH=join(dirname(__file__), '../data/datastore'))
class TestDatastore(TestCase):
    def test_check_for_new_events(self):
        """Finds the test data file and the station's tables inside"""

        # Pretend last check was long ago
        last_check_time = time.mktime(datetime.datetime(2010, 1, 1).timetuple())
        event_summary = datastore.check_for_new_events(last_check_time)
        self.assertEqual(
            {
                datetime.date(2017, 1, 1): {
                    501: {
                        'blobs': 687,
                        'singles': 301,
                        'weather': 60,
                        'satellites': 0,
                        'singles_old': 86400,
                        'config': 1,
                        'events': 168,
                    }
                }
            },
            event_summary,
        )

    def test_get_stations(self):
        """Get all stations with a node in the test data"""

        self.assertEqual([501], datastore.get_stations(datetime.date(2017, 1, 1)))

    def test_get_data_path(self):
        """Get all stations with a node in the test data"""

        self.assertEqual(
            join(settings.DATASTORE_PATH, '2017/1/2017_1_1.h5'),
            datastore.get_data_path(datetime.date(2017, 1, 1)),
        )

    def test_get_config_messages(self):
        """Get all stations with a node in the test data"""
        try:
            result = datastore.get_config_messages('amsterdam', 501, datetime.date(2017, 1, 1))
            station_node = result[0].root.hisparc.cluster_amsterdam.station_501

            self.assertEqual((result[0], station_node.config, station_node.blobs), result)
        finally:
            result[0].close()
