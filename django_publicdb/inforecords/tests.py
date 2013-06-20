# Python
import datetime
import re
import code

import urllib

# Django
from django.conf import settings
from django.test import LiveServerTestCase

# Publicdb
from django_publicdb.inforecords.models import *

def is_plaintext(response):

    for left, right in [
        (response.getcode(),            200),
        (response.info().getmaintype(), "text"),
        (response.info().getsubtype(),  "plain")
    ]:
        if left != right:
            return False

    return True


class ViewsTestCase(LiveServerTestCase):
    fixtures = [
        'tests_inforecords'
    ]

    #---------------------------------------------------------------------------
    # Setup and teardown
    #---------------------------------------------------------------------------

    def setUp(self):
        super(ViewsTestCase, self).setUp()


    def tearDown(self):
        super(ViewsTestCase, self).tearDown()

    #---------------------------------------------------------------------------
    # Helper functions
    #---------------------------------------------------------------------------

    def check_and_get_response(self, url):
        response = urllib.urlopen("%s%s%s" %(
                                  self.live_server_url,
                                  "",
                                  url))

        self.assertTrue(is_plaintext(response))

        return response

    #---------------------------------------------------------------------------
    # Tests
    #---------------------------------------------------------------------------

    def test_config_nagios(self):
        self.check_and_get_response("/config/nagios")

    def test_config_datastore(self):
        self.check_and_get_response("/config/datastore")


class NagiosTestCase(LiveServerTestCase):
    fixtures = [
        'tests_inforecords',
        'tests_histograms'
    ]

    #---------------------------------------------------------------------------
    # Setup and teardown
    #---------------------------------------------------------------------------

    def setUp(self):
        super(NagiosTestCase, self).setUp()

        Pc.objects.exclude(station__number=501).delete()
        Station.objects.exclude(number=501).delete()

    def tearDown(self):
        super(NagiosTestCase, self).tearDown()

    #---------------------------------------------------------------------------
    # Helper functions
    #---------------------------------------------------------------------------

    def check_and_get_response(self, url):
        response = urllib.urlopen("%s%s%s" %(
                                  self.live_server_url,
                                  "",
                                  url))

        self.assertTrue(is_plaintext(response))

        return response

    #---------------------------------------------------------------------------
    # Tests
    #---------------------------------------------------------------------------

    def test_config_nagios(self, ):
        response = self.check_and_get_response("/config/nagios")
        text = response.read()

        # Station 501 has four plates, thus four services are expected

        pulseheight_mpv_services = re.findall(
            'define service{.*?Pulseheight MPV.*?}',
            text, re.S
        )
        self.assertEqual(len(pulseheight_mpv_services), 4)
