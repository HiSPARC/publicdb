# Python
import datetime

import json
import urllib

# Django
from django.conf import settings
from django.test import LiveServerTestCase

# Publicdb
from django_publicdb.tests import datastore as tests_datastore
from django_publicdb.inforecords.models import *
from django_publicdb.histograms.models import *

def is_html(response):

    for left, right in [
        (response.getcode(),            200),
        (response.info().getmaintype(), "text"),
        (response.info().getsubtype(),  "html")
    ]:
        if left != right:
            return False

    return True


class ViewsTestCase(LiveServerTestCase):
    fixtures = [
        'tests_inforecords',
        'tests_histograms'
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
                                  "/show",
                                  url))

        self.assertTrue(is_html(response))

        return response

    #---------------------------------------------------------------------------
    # Tests
    #---------------------------------------------------------------------------

    def test_stations(self):
        self.check_and_get_response("/stations")

    def test_stations_by_country(self):
        self.check_and_get_response("/stations_by_country")

    def test_stations_by_name(self):
        self.check_and_get_response("/stations_by_name")

    def test_stations_by_number(self):
        self.check_and_get_response("/stations_by_number")

    def test_stations_on_map(self):
        self.check_and_get_response("/stations_on_map")
        self.check_and_get_response("/stations_on_map/Netherlands")
        self.check_and_get_response("/stations_on_map/Netherlands/Amsterdam")
        self.check_and_get_response("/stations_on_map/Netherlands/Amsterdam/Alkmaar")

    def test_station(self):
        self.check_and_get_response("/stations/501")

    def test_stations_data(self):
        self.check_and_get_response("/stations/501/2011/7/7")

    def test_stations_status(self):
        self.check_and_get_response("/stations/501/status")

    def test_stations_config(self):
        self.check_and_get_response("/stations/501/config")

    def test_get_eventtime_histogram_source(self):
        self.check_and_get_response("/source/eventtime/2011/7/7")

    def test_get_pulseheight_histogram_source(self):
        self.check_and_get_response("/source/pulseheight/2011/7/7")

    def test_get_pulseintegral_histogram_source(self):
        self.check_and_get_response("/source/pulseintegral/2011/7/7")

    def test_get_barometer_dataset_source(self):
        self.check_and_get_response("/source/barometer/2011/7/7")

    def test_get_temperature_dataset_source(self):
        self.check_and_get_response("/source/temperature/2011/7/7")

    def test_get_voltage_config_source(self):
        self.check_and_get_response("/source/voltage/501")

    def test_get_current_config_source(self):
        self.check_and_get_response("/source/current/501")

    def test_get_gps_config_source(self):
        self.check_and_get_response("/source/gps/501")

    def test_help(self):
        self.check_and_get_response("/help")

