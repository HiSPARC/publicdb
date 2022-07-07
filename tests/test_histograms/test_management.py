from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class TestManagement(TestCase):
    @patch('publicdb.histograms.checks.check_for_updates', return_value=False)
    @patch('publicdb.histograms.jobs.update_all_histograms', return_value=False)
    def test_updatehistograms(self, mock_update_histograms, mock_check):
        """The command tried to check for updates and update the histograms"""

        call_command('updatehistograms')

        # The check for updates and update histograms are only called once
        mock_check.assert_called_once_with()
        mock_update_histograms.assert_called_once_with()
