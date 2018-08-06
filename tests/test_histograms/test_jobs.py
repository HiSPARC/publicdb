from datetime import date
from os.path import abspath, dirname, join
from shutil import rmtree
from tempfile import mkdtemp

from mock import patch

from django.conf import settings
from django.test import TestCase, override_settings

from sapphire.tests.validate_results import validate_results

from publicdb.histograms import jobs, models

from ..factories import histograms_factories, inforecords_factories


@override_settings(DATASTORE_PATH=join(dirname(abspath(__file__)), 'test_data/datastore'))
class TestJobs(TestCase):

    @patch('django.db.close_old_connections')
    @patch('publicdb.histograms.jobs.perform_update_tasks')
    def test_update_all_histograms(self, mock_perform, mock_close):
        """The update function is called if previous check has finished"""

        self.assertTrue(jobs.update_all_histograms())
        mock_perform.assert_called_once_with()

    @patch('publicdb.histograms.jobs.perform_update_tasks')
    def test_update_all_histograms_still_running(self, mock_perform):
        """The update function is not called if a previous check has not finished"""

        state = models.GeneratorState.objects.get()
        state.update_is_running = True
        state.save()

        self.assertFalse(jobs.update_all_histograms())
        self.assertFalse(mock_perform.called)

    def setup_station(self):
        cluster = inforecords_factories.ClusterFactory(name='Amsterdam', number=0, country__number=0)
        self.station = inforecords_factories.StationFactory(number=501, cluster=cluster)

    @patch('django.db.close_old_connections')
    @override_settings(ESD_PATH=mkdtemp())
    def test_perform_update_tasks(self, mock_close):
        """Update the ESD for summaries in need of updates"""

        self.setup_station()
        histograms_factories.SummaryFactory(
            station=self.station, date=date(2017, 1, 1),
            needs_update_events=True, num_events=168,
            needs_update_weather=True, num_weather=60,
            needs_update_config=True, num_config=None,
            needs_update_singles=True, num_singles=301,
            needs_update=True,
        )

        jobs.perform_update_tasks()

        test_data = join(settings.ESD_PATH, '2017/1/2017_1_1.h5')
        reference_path = join(dirname(abspath(__file__)), 'test_data/esd/2017/1/2017_1_1.h5')
        validate_results(self, test_data, reference_path)
        rmtree(settings.ESD_PATH)

        self.assertEqual(1, models.Configuration.objects.all().count())