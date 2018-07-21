from mock import patch

from django.test import TestCase

from publicdb.histograms import jobs, models


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
