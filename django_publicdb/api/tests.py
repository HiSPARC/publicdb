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

def is_json(response):

    for left, right in [
        (response.getcode(),            200),
        (response.info().getmaintype(), "application"),
        (response.info().getsubtype(),  "json")
    ]:
        if left != right:
            return False

    return True


class MyAPItests(LiveServerTestCase):
    fixtures = [
        'tests_inforecords',
        'tests_histograms'
    ]

    #---------------------------------------------------------------------------
    # Setup and teardown
    #---------------------------------------------------------------------------

    def setUp(self):
        super(MyAPItests, self).setUp()


    def tearDown(self):
        super(MyAPItests, self).tearDown()

    #---------------------------------------------------------------------------
    # Helper functions
    #---------------------------------------------------------------------------

    def check_and_get_response(self, url):
        response = urllib.urlopen("%s%s%s" %(
                                  self.live_server_url,
                                  "/api",
                                  url))

        assert(is_json(response))

        return response

    #---------------------------------------------------------------------------
    # Tests
    #---------------------------------------------------------------------------

    def test_station_501(self, ):
        self.check_and_get_response("/station/501")

        self.check_and_get_response("/station/501/data/")
        self.check_and_get_response("/station/501/data/2011/9/9")

        self.check_and_get_response("/station/501/weather/")
        self.check_and_get_response("/station/501/weather/2011/9/9")

        self.check_and_get_response("/station/501/config/")
        self.check_and_get_response("/station/501/config/2011/9/9")

        self.check_and_get_response("/station/501/num_events/")
        self.check_and_get_response("/station/501/num_events/2011")
        self.check_and_get_response("/station/501/num_events/2011/9")
        self.check_and_get_response("/station/501/num_events/2011/9/9")

        response = self.check_and_get_response("/station/501/plate/1/pulseheight/fit/2011/7/7")
        json_data = json.loads(response.read())
        assert(
            json_data["year"] == 2011 and
            json_data["month"] == 7 and
            json_data["day"] == 7 and
            json_data["fitted_mpv"] == 222.101846139
        )

        self.check_and_get_response("/station/501/plate/1/pulseheight/drift/2011/9/1/30")


    def test_stations(self):
        self.check_and_get_response("/stations/")
        self.check_and_get_response("/stations/data/")
        self.check_and_get_response("/stations/data/2011")
        self.check_and_get_response("/stations/data/2011/9")
        self.check_and_get_response("/stations/data/2011/9/9")
        self.check_and_get_response("/stations/weather/")
        self.check_and_get_response("/stations/weather/2011/")
        self.check_and_get_response("/stations/weather/2011/9")
        self.check_and_get_response("/stations/weather/2011/9/9")


    def test_subclusters(self):
        response = self.check_and_get_response("/subclusters/")

        json_data = json.loads(response.read())
        response = self.check_and_get_response("/subclusters/%d" % json_data[0]["number"])


    def test_clusters(self):
        response = self.check_and_get_response("/clusters/")

        json_data = json.loads(response.read())
        response = self.check_and_get_response("/clusters/%d" % json_data[0]["number"])


    def test_countries(self):
        response = self.check_and_get_response("/countries/")

        json_data = json.loads(response.read())
        response = self.check_and_get_response("/countries/%d" % json_data[0]["number"])

