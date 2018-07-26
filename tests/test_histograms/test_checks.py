from datetime import date, datetime
from mock import Mock, patch

from django.test import TestCase

from publicdb.histograms import checks, models

from ..factories import histograms_factories, inforecords_factories


class TestChecks(TestCase):

    @patch('publicdb.histograms.checks.check_for_new_events_and_update_flags')
    def test_check_for_updates(self, mock_flags):
        """The check function is called if previous check has finished"""

        self.assertTrue(checks.check_for_updates())
        state = models.GeneratorState.objects.get()
        mock_flags.assert_called_once_with(state)

    @patch('publicdb.histograms.checks.check_for_new_events_and_update_flags')
    def test_check_for_updates_still_running(self, mock_flags):
        """The check function is not called if a previous check has not finished"""

        state = models.GeneratorState.objects.get()
        state.check_is_running = True
        state.save()

        self.assertFalse(checks.check_for_updates())
        self.assertFalse(mock_flags.called)

    def setup_station(self):
        cluster = inforecords_factories.ClusterFactory(name='Amsterdam', number=0, country__number=0)
        self.station = inforecords_factories.StationFactory(number=501, cluster=cluster)

    @patch('publicdb.histograms.datastore.check_for_new_events')
    def test_check_for_new_events_and_update_flags_creates_summaries(self, mock_events):
        mock_events.return_value = {
            date(2017, 1, 1): {
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
        }
        self.setup_station()
        state = Mock(check_last_run=datetime(2004, 1, 1, 1, 0, 0))

        checks.check_for_new_events_and_update_flags(state)
        state.save.assert_called()
        self.assertFalse(state.check_is_running)
        self.assertGreater(state.check_last_run, datetime(2004, 1, 1, 1, 0, 0))

        summary = models.Summary.objects.get(station=self.station, date=date(2017, 1, 1))
        self.assertEqual(summary.num_events, 168)
        self.assertTrue(summary.needs_update_events)
        self.assertEqual(summary.num_weather, 60)
        self.assertTrue(summary.needs_update_weather)
        self.assertIsNone(summary.num_config)  # Not set 'early'
        self.assertTrue(summary.needs_update_config)
        self.assertEqual(summary.num_singles, 301)
        self.assertTrue(summary.needs_update_singles)

        network_summary = models.NetworkSummary.objects.get(date=date(2017, 1, 1))
        self.assertTrue(network_summary.needs_update_coincidences)

    @patch('publicdb.histograms.datastore.check_for_new_events')
    def test_check_for_new_events_and_update_flags_updates_summaries(self, mock_events):
        mock_events.return_value = {
            date(2017, 1, 1): {
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
        }
        self.setup_station()
        summary = histograms_factories.SummaryFactory(
            station=self.station, date=date(2017, 1, 1),
            num_events=100, needs_update_events=False,
            num_weather=None, needs_update_weather=False,
            num_config=None, needs_update_config=False,
            num_singles=10, needs_update_singles=False,
        )

        state = Mock(check_last_run=datetime(2004, 1, 1, 1, 0, 0))

        checks.check_for_new_events_and_update_flags(state)
        state.save.assert_called()
        self.assertFalse(state.check_is_running)
        self.assertGreater(state.check_last_run, datetime(2004, 1, 1, 1, 0, 0))

        summary.refresh_from_db()
        self.assertEqual(summary.num_events, 168)
        self.assertTrue(summary.needs_update_events)
        self.assertEqual(summary.num_weather, 60)
        self.assertTrue(summary.needs_update_weather)
        self.assertIsNone(summary.num_config)  # Not set 'early'
        self.assertTrue(summary.needs_update_config)
        self.assertEqual(summary.num_singles, 301)
        self.assertTrue(summary.needs_update_singles)

        network_summary = models.NetworkSummary.objects.get(date=date(2017, 1, 1))
        self.assertTrue(network_summary.needs_update_coincidences)
