from datetime import date, timedelta

from django.test import Client, TestCase
from django.urls import reverse

from ..factories.histograms_factories import ConfigurationFactory, DailyHistogramFactory, SummaryFactory
from ..factories.inforecords_factories import StationFactory


class ViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.station = StationFactory(number=1, cluster__number=0, cluster__country__number=0)
        self.summary = SummaryFactory(station=self.station)
        self.data = DailyHistogramFactory(source=self.summary, type__slug='eventtime')
        self.config = ConfigurationFactory(source=self.summary)
        super(ViewsTestCase, self).setUp()

    def get_tsv(self, url):
        """Get url and check if the response is OK and valid json"""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/tab-separated-values', response['Content-Type'])
        return response

    def get_html(self, url):
        """Get url and check if the response is OK and valid json"""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])
        return response

    def test_stations(self):
        response = self.client.get(reverse('status:stations'))
        self.assertEqual(302, response.status_code)
        self.assertEqual(reverse('status:stations_by_country'), response['Location'])

    def test_stations_by_country(self):
        self.get_html(reverse('status:stations_by_country'))

    def test_stations_by_name(self):
        self.get_html(reverse('status:stations_by_name'))

    def test_stations_by_number(self):
        self.get_html(reverse('status:stations_by_number'))

    def test_stations_on_map(self):
        self.get_html(reverse('status:map:stations_on_map'))
        kwargs = {'country': self.station.cluster.country.name}
        self.get_html(reverse('status:map:stations_on_map', kwargs=kwargs))
        kwargs.update({'cluster': self.station.cluster.name})
        self.get_html(reverse('status:map:stations_on_map', kwargs=kwargs))
        kwargs.update({'subcluster': self.station.cluster.name})
        self.get_html(reverse('status:map:stations_on_map', kwargs=kwargs))

    def test_station(self):
        kwargs = {'station_number': self.station.number}
        response = self.client.get(reverse('status:station:data', kwargs=kwargs))
        self.assertEqual(302, response.status_code)
        kwargs = {
            'station_number': self.station.number,
            'year': self.summary.date.year,
            'month': self.summary.date.month,
            'day': self.summary.date.day,
        }
        self.assertEqual(reverse('status:station:data', kwargs=kwargs), response['Location'])

    def test_stations_data(self):
        kwargs = {
            'station_number': self.station.number,
            'year': self.summary.date.year,
            'month': self.summary.date.month,
            'day': self.summary.date.day,
        }
        self.get_html(reverse('status:station:data', kwargs=kwargs))

    def test_help(self):
        self.get_html(reverse('status:help'))
