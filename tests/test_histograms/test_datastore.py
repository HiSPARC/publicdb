import datetime
import time

from os.path import join, dirname, abspath

from django.test import TestCase, override_settings

from publicdb.histograms import datastore


@override_settings(DATASTORE_PATH=join(dirname(abspath(__file__)), 'test_data/datastore'))
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
                        'events': 168
                    }
                }
            },
            event_summary)
