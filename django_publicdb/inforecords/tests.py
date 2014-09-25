import datetime
import re
import code
import os
import subprocess
import urllib
import inspect

from django.conf import settings
from django.test import LiveServerTestCase
from django.test.utils import override_settings

from django_publicdb.inforecords.models import *
from django_publicdb.histograms.models import *
from scripts.nagios.check_pulseheight_mpv import check_pulseheight_mpv


def is_plaintext(response):
    """Check if the response is OK and of type text/plain"""

    for left, right in [(response.getcode(), 200),
                        (response.info().getmaintype(), "text"),
                        (response.info().getsubtype(), "plain")]:
        if left != right:
            return False

    return True


def check_and_get_response(testcase, url):
    response = urllib.urlopen("%s%s%s" % (testcase.live_server_url, "", url))

    testcase.assertTrue(is_plaintext(response))

    return response


class ViewsTestCase(LiveServerTestCase):
    fixtures = ['tests_inforecords']

    def setUp(self):
        super(ViewsTestCase, self).setUp()

    def tearDown(self):
        super(ViewsTestCase, self).tearDown()

    def test_config_nagios(self):
        check_and_get_response(self, "/config/nagios")

    def test_config_datastore(self):
        check_and_get_response(self, "/config/datastore")


class NagiosConfigTestCase(LiveServerTestCase):
    fixtures = ['tests_inforecords', 'tests_histograms']

    def setUp(self):
        super(NagiosConfigTestCase, self).setUp()

    def tearDown(self):
        super(NagiosConfigTestCase, self).tearDown()

    def test_config_nagios_501(self):
        """ Tests the generated nagios config file for station 501.

        This checks the following things:
        - Number of services for checking the detectors. This should
          correspond to the number of detectors of the station.
        - Definition of the command referenced by the service.
        - The existence of the file referenced by the command.
        - Return status of the file when executed. This should
          return exit status 3 (UNKNOWN in terms of nagios).

        """
        # Initialize work space

        Pc.objects.exclude(station__number=501).delete()
        Station.objects.exclude(number=501).delete()
        PulseheightFit.objects.all().delete()

        response = check_and_get_response(self, "/config/nagios")
        text = response.read()

        # Station 501 has four detectors, thus four services are expected

        services = re.findall('define service\s*?{.*?}', text, re.S)

        pulseheight_mpv_services = [service for service in services
                                    if service.count("Pulseheight MPV") > 0]

        self.assertEqual(len(pulseheight_mpv_services), 4)

        # Character count should be the same for all four of them

        char_count = len(pulseheight_mpv_services[0])

        for service in pulseheight_mpv_services:
            self.assertEqual(len(service), char_count)

        # Extract check_command

        search_result = re.search('check_command\s+(.+?)\n',
                                  pulseheight_mpv_services[0])

        check_command = search_result.group(1)
        command_name = search_result.group(1).split("!")[0]
        command_args = search_result.group(1).split("!")[1:]

        # Check if the command check_pulseheight_mpv is defined

        search_result = re.search(
            'define command\s*?{\s*?command_name\s+?%s\s+?' % command_name +
            'command_line\s+?(.*?)\s.*?}',
            text, re.S)
        self.assertIsNotNone(search_result)

        # Check if the check_pulseheight_mpv.py script can be found
        # FIXME: This will fail, except on the Nagios server..
        # script = search_result.group(1)
        # self.assertTrue(os.path.exists(script))


class NagiosPluginTestCase(LiveServerTestCase):
    fixtures = ['tests_inforecords', 'tests_histograms']

    def setUp(self):
        super(NagiosPluginTestCase, self).setUp()

        settings.PUBLICDB_HOST_FOR_NAGIOS = self.live_server_url

    def tearDown(self):
        super(NagiosPluginTestCase, self).tearDown()

    def test_plugin_wrong_arguments(self):
        """ Tests the check_pulseheight_mpv plugin in case of wrong arguments
            Should return exit code 3 (UNKNOWN).
            Executes the plugin via subprocess.
        """

        # Should return exit code 3, which stands for UNKNOWN to nagios.
        # Should return exit code 3 because no fit has been found.

        with open(os.devnull, "w") as devnull:
            returncode = subprocess.call(
                [inspect.getsourcefile(check_pulseheight_mpv), ""],
                stdout=devnull, shell=True)
            self.assertEqual(returncode, 3)

            returncode = subprocess.call(
                [inspect.getsourcefile(check_pulseheight_mpv), "501"],
                stdout=devnull, shell=True)
            self.assertEqual(returncode, 3)

            returncode = subprocess.call(
                [inspect.getsourcefile(check_pulseheight_mpv), "blala lalaa"],
                stdout=devnull, shell=True)
            self.assertEqual(returncode, 3)

    def test_plugin_no_fit(self):
        """ Tests the check_pulseheight_mpv plugin in case of no fit found.
            Should return exit code 3 (UNKNOWN).
            Executes the plugin via subprocess.
        """

        # Initialize work space

        PulseheightFit.objects.all().delete()

        # Should return exit code 3, which stands for UNKNOWN to nagios.
        # Should return exit code 3 because no fit has been found.

        with open(os.devnull, "w") as devnull:
            returncode = subprocess.call(
                [inspect.getsourcefile(check_pulseheight_mpv), "501 1"],
                stdout=devnull, shell=True)
            self.assertEqual(returncode, 3)

    def test_plugin_fit_within_thresholds(self):
        """ Tests the check_pulseheight_mpv plugin in case of a fit
            within thresholds. Should return exit code 0 (OK).
        """

        # Initialize work space
        # Delete all fits. Then insert one fit that is within thresholds.

        PulseheightFit.objects.all().delete()

        summary = Summary.objects.get(station__number=501,
                                      date=datetime.date(2011, 7, 7))

        thresholds = MonitorPulseheightThresholds.objects.filter(station=summary.station)
        threshold = thresholds[1]

        fit = PulseheightFit(source=summary,
                             plate=threshold.plate,
                             initial_mpv=threshold.mpv_mean,
                             initial_width=50,
                             fitted_mpv=threshold.mpv_mean,
                             fitted_mpv_error=threshold.mpv_mean * 0.01,
                             fitted_width=threshold.mpv_sigma,
                             fitted_width_error=threshold.mpv_sigma * 0.01,
                             chi_square_reduced=1)

        fit.save()

        # Should return exit code 0, which stands for OK to nagios.
        # Should return exit code 0 because a fit has been found and it is
        # within thresholds

        status, message = check_pulseheight_mpv(self.live_server_url,
                                                summary.station.number,
                                                threshold.plate,
                                                summary.date)
        self.assertEqual(status[0], 0)

    def test_plugin_fit_below_thresholds(self):
        """ Tests the check_pulseheight_mpv plugin in case of a fit
            below thresholds. Should return exit code 2 (CRITICAL).
        """

        # Initialize work space
        # Delete all fits. Then insert one fit that is below thresholds.

        PulseheightFit.objects.all().delete()

        summary = Summary.objects.get(station__number=501,
                                      date=datetime.date(2011, 7, 7))

        thresholds = MonitorPulseheightThresholds.objects.filter(station=summary.station)
        threshold = thresholds[1]

        fit = PulseheightFit(source=summary,
                             plate=threshold.plate,
                             initial_mpv=threshold.mpv_mean * 0.2,
                             initial_width=50,
                             fitted_mpv=threshold.mpv_mean * 0.3,
                             fitted_mpv_error=threshold.mpv_mean * 0.3 * 0.01,
                             fitted_width=threshold.mpv_sigma,
                             fitted_width_error=threshold.mpv_sigma * 0.01,
                             chi_square_reduced=1)

        fit.save()

        # Should return exit code 2, which stands for CRITICAL to nagios.
        # Should return exit code 2 because a fit has been found but it is
        # below thresholds

        status, message = check_pulseheight_mpv(self.live_server_url,
                                                summary.station.number,
                                                threshold.plate,
                                                summary.date)
        self.assertEqual(status[0], 2)

    def test_plugin_fit_above_thresholds(self):
        """ Tests the check_pulseheight_mpv plugin in case of a fit
            above thresholds. Should return exit code 2 (CRITICAL).
        """

        # Initialize work space
        # Delete all fits. Then insert one fit that is above thresholds.

        PulseheightFit.objects.all().delete()

        summary = Summary.objects.get(station__number=501,
                                      date=datetime.date(2011, 7, 7))

        thresholds = MonitorPulseheightThresholds.objects.filter(station=summary.station)
        threshold = thresholds[1]

        fit = PulseheightFit(source=summary,
                             plate=threshold.plate,
                             initial_mpv=threshold.mpv_mean * 2.2,
                             initial_width=50,
                             fitted_mpv=threshold.mpv_mean * 2.3,
                             fitted_mpv_error=threshold.mpv_mean * 2.3 * 0.01,
                             fitted_width=threshold.mpv_sigma,
                             fitted_width_error=threshold.mpv_sigma * 0.01,
                             chi_square_reduced=1)

        fit.save()

        # Should return exit code 2, which stands for CRITICAL to nagios.
        # Should return exit code 2 because a fit has been found but it is
        # above thresholds

        status, message = check_pulseheight_mpv(self.live_server_url,
                                                summary.station.number,
                                                threshold.plate,
                                                summary.date)
        self.assertEqual(status[0], 2)
