from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from ..factories import histograms_factories
from ..factories.inforecords_factories import StationFactory


@patch('publicdb.status_display.nagios.status_lists', return_value=([], [], []))
class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.station = StationFactory(number=1, cluster__number=0, cluster__country__number=0)
        self.summary = histograms_factories.SummaryFactory(station=self.station)
        self.config = histograms_factories.ConfigurationFactory(summary=self.summary)
        super().setUp()

    def get_html(self, url):
        """Get url and check if the response is OK and valid json"""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])
        return response

    def test_station_on_map(self, mock_status):
        kwargs = {'station_number': self.station.number}
        self.get_html(reverse('maps:map', kwargs=kwargs))

    def test_all_stations_on_map(self, mock_status):
        self.get_html(reverse('maps:map'))

    def test_stations_on_map(self, mock_status):
        kwargs = {'country': self.station.cluster.country.name}
        self.get_html(reverse('maps:map', kwargs=kwargs))
        kwargs.update({'cluster': self.station.cluster.main_cluster()})
        self.get_html(reverse('maps:map', kwargs=kwargs))
        kwargs.update({'subcluster': self.station.cluster.name})
        self.get_html(reverse('maps:map', kwargs=kwargs))
