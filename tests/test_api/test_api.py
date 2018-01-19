import datetime
import json
import urllib

from django.conf import settings
from django.test import LiveServerTestCase

from lib.test import datastore as test_datastore

from publicdb.histograms.models import *
from publicdb.inforecords.models import *


def is_json(response):
    """Check if the response is OK and of type application/json"""

    for left, right in [(response.getcode(), 200),
                        (response.info().getmaintype(), "application"),
                        (response.info().getsubtype(), "json")]:
        if left != right:
            return False

    return True


class ViewsTestCase(LiveServerTestCase):
    fixtures = ['tests_inforecords', 'tests_histograms']

    def check_and_get_response(self, url):
        response = urllib.urlopen("%s/api%s" % (self.live_server_url, url))

        self.assertTrue(is_json(response))

        return response

    def test_station_501(self, ):
        self.check_and_get_response("/station/501/")

        self.check_and_get_response("/station/501/data/")
        self.check_and_get_response("/station/501/data/2011/")
        self.check_and_get_response("/station/501/data/2011/9/")
        self.check_and_get_response("/station/501/data/2011/9/9/")

        self.check_and_get_response("/station/501/weather/")
        self.check_and_get_response("/station/501/weather/2011/")
        self.check_and_get_response("/station/501/weather/2011/9/")
        self.check_and_get_response("/station/501/weather/2011/9/9/")

        self.check_and_get_response("/station/501/config/")
        self.check_and_get_response("/station/501/config/2011/9/9/")

        self.check_and_get_response("/station/501/num_events/")
        self.check_and_get_response("/station/501/num_events/2011/")
        self.check_and_get_response("/station/501/num_events/2011/9/")
        self.check_and_get_response("/station/501/num_events/2011/9/9/")

        response = self.check_and_get_response("/station/501/plate/1/pulseheight/fit/2011/7/7/")
        json_data = json.loads(response.read())
        assert(json_data["year"] == 2011 and
               json_data["month"] == 7 and
               json_data["day"] == 7 and
               json_data["fitted_mpv"] == 222.101846139)

        self.check_and_get_response("/station/501/plate/1/pulseheight/drift/2011/9/1/30/")
        self.check_and_get_response("/station/501/plate/1/pulseheight/drift/last_14_days/")
        self.check_and_get_response("/station/501/plate/1/pulseheight/drift/last_30_days/")

    def test_stations(self):
        self.check_and_get_response("/stations/")

        self.check_and_get_response("/stations/data/")
        self.check_and_get_response("/stations/data/2011/")
        self.check_and_get_response("/stations/data/2011/9/")
        self.check_and_get_response("/stations/data/2011/9/9/")

        self.check_and_get_response("/stations/weather/")
        self.check_and_get_response("/stations/weather/2011/")
        self.check_and_get_response("/stations/weather/2011/9/")
        self.check_and_get_response("/stations/weather/2011/9/9/")

    def test_subclusters(self):
        response = self.check_and_get_response("/subclusters/")

        json_data = json.loads(response.read())
        response = self.check_and_get_response("/subclusters/%d" %
                                               json_data[0]["number"])

    def test_clusters(self):
        response = self.check_and_get_response("/clusters/")

        json_data = json.loads(response.read())
        response = self.check_and_get_response("/clusters/%d" %
                                               json_data[0]["number"])

    def test_countries(self):
        response = self.check_and_get_response("/countries/")

        json_data = json.loads(response.read())
        response = self.check_and_get_response("/countries/%d" %
                                               json_data[0]["number"])
