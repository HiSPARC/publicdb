from mock import patch

from django.test import TestCase

from publicdb.histograms import jobs, models


class TestJobs(TestCase):
    @patch('publicdb.histograms.jobs.check_for_new_events_and_update_flags')
    def test_check_for_updates(self, mock_flags):
        """The check function is called if previous check has finished"""

        self.assertTrue(jobs.check_for_updates())
        state = models.GeneratorState.objects.get()
        mock_flags.assert_called_once_with(state)

    @patch('publicdb.histograms.jobs.check_for_new_events_and_update_flags')
    def test_check_for_updates_still_running(self, mock_flags):
        """The check function is not called if a previous check has not finished"""

        state = models.GeneratorState.objects.get()
        state.check_is_running = True
        state.save()

        self.assertFalse(jobs.check_for_updates())
        self.assertFalse(mock_flags.called)

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
