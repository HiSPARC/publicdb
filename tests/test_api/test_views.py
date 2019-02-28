from datetime import date, timedelta

from django.test import Client, TestCase
from django.urls import reverse

from ..factories.histograms_factories import ConfigurationFactory
from ..factories.inforecords_factories import PcFactory, StationFactory
from ..utils import date_as_kwargs


class TestViews(TestCase):

    """Test if all endpoints work and sometimes that the expected data is returned"""

    def setUp(self):
        self.client = Client()
        self.station = StationFactory(number=1, cluster__number=0, cluster__country__number=0)
        self.config = ConfigurationFactory(summary__station=self.station)
        self.pc = PcFactory(station=self.station, is_test=False)
        super(TestViews, self).setUp()

    def get_json(self, url):
        """Get url and check if the response is OK and valid json"""
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        return response.json()

    def assert_not_found(self, url):
        """Get url and check if the response is NOT FOUND"""
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_man(self):
        self.get_json(reverse('api:man'))

    def test_station(self):
        kwargs = {'station_number': self.station.number}
        self.get_json(reverse('api:station', kwargs=kwargs))
        self.get_json(reverse('api:has_data', kwargs=kwargs))
        self.get_json(reverse('api:has_weather', kwargs=kwargs))
        self.get_json(reverse('api:num_events', kwargs=kwargs))
        self.get_json(reverse('api:config', kwargs=kwargs))

        kwargs.update({'year': 2011})
        self.get_json(reverse('api:has_data', kwargs=kwargs))
        self.get_json(reverse('api:has_weather', kwargs=kwargs))
        self.get_json(reverse('api:num_events', kwargs=kwargs))

        kwargs.update({'month': 9})
        self.get_json(reverse('api:has_data', kwargs=kwargs))
        self.get_json(reverse('api:has_weather', kwargs=kwargs))
        self.get_json(reverse('api:num_events', kwargs=kwargs))

        kwargs.update({'day': 5})
        self.get_json(reverse('api:station', kwargs=kwargs))
        self.get_json(reverse('api:has_data', kwargs=kwargs))
        self.get_json(reverse('api:has_weather', kwargs=kwargs))
        self.get_json(reverse('api:num_events', kwargs=kwargs))

        kwargs.update({'hour': 14})
        self.get_json(reverse('api:num_events', kwargs=kwargs))

        config_date = self.config.summary.date
        kwargs = {'station_number': self.station.number}
        kwargs.update(date_as_kwargs(config_date))
        self.get_json(reverse('api:config', kwargs=kwargs))

        # Invalid station
        kwargs = {'station_number': 1337}
        self.assert_not_found(reverse('api:station', kwargs=kwargs))
        self.assert_not_found(reverse('api:has_data', kwargs=kwargs))
        self.assert_not_found(reverse('api:has_weather', kwargs=kwargs))
        self.assert_not_found(reverse('api:num_events', kwargs=kwargs))

    def test_stations(self):
        data = self.get_json(reverse('api:stations'))
        self.assertEqual([{'number': 1, 'name': self.station.name}], data)
        self.get_json(reverse('api:data_stations'))
        self.get_json(reverse('api:weather_stations'))

        kwargs = {'year': 2011}
        self.get_json(reverse('api:data_stations', kwargs=kwargs))
        self.get_json(reverse('api:weather_stations', kwargs=kwargs))

        kwargs.update({'month': 9})
        self.get_json(reverse('api:data_stations', kwargs=kwargs))
        self.get_json(reverse('api:weather_stations', kwargs=kwargs))

        kwargs.update({'day': 5})
        self.get_json(reverse('api:data_stations', kwargs=kwargs))
        self.get_json(reverse('api:weather_stations', kwargs=kwargs))

        # Invalid dates
        tomorrow = date.today() + timedelta(days=1)
        kwargs = date_as_kwargs(tomorrow)
        self.assert_not_found(reverse('api:data_stations', kwargs=kwargs))
        self.assert_not_found(reverse('api:weather_stations', kwargs=kwargs))

        before_hisparc = date(2003, 12, 30)
        kwargs = date_as_kwargs(before_hisparc)
        self.assert_not_found(reverse('api:data_stations', kwargs=kwargs))
        self.assert_not_found(reverse('api:weather_stations', kwargs=kwargs))

    def test_subclusters(self):
        data = self.get_json(reverse('api:subclusters'))
        self.assertEqual([{'number': 0, 'name': self.station.cluster.name}], data)

        kwargs = {'subcluster_number': self.station.cluster.number}
        data = self.get_json(reverse('api:stations', kwargs=kwargs))
        self.assertEqual([{'number': 1, 'name': self.station.name}], data)

        # Non existant subcluster number
        kwargs = {'subcluster_number': 1337}
        self.assert_not_found(reverse('api:stations', kwargs=kwargs))

    def test_clusters(self):
        data = self.get_json(reverse('api:clusters'))
        self.assertEqual([{'number': 0, 'name': self.station.cluster.name}], data)

        kwargs = {'cluster_number': self.station.cluster.number}
        data = self.get_json(reverse('api:subclusters', kwargs=kwargs))
        self.assertEqual([{'number': 0, 'name': self.station.cluster.name}], data)

        # Non existant cluster number
        kwargs = {'cluster_number': 1337}
        self.assert_not_found(reverse('api:subclusters', kwargs=kwargs))

    def test_countries(self):
        data = self.get_json(reverse('api:countries'))
        self.assertEqual([{'number': 0, 'name': self.station.cluster.country.name}], data)

        kwargs = {'country_number': self.station.cluster.country.number}
        data = self.get_json(reverse('api:clusters', kwargs=kwargs))
        self.assertEqual([{'number': 0, 'name': self.station.cluster.name}], data)

        # Non existant country number
        kwargs = {'country_number': 1337}
        self.assert_not_found(reverse('api:clusters', kwargs=kwargs))
