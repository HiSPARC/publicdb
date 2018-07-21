from mock import patch

from django.test import TestCase

from publicdb.histograms import checks, models


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
