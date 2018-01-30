from io import StringIO

from numpy import genfromtxt

from django.test import Client, TestCase
from django.urls import reverse

from ..factories import histograms_factories
from ..factories.inforecords_factories import StationFactory
from ..factories.station_layout_factories import StationLayoutFactory
from ..utils import date_as_kwargs


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.station = StationFactory(number=1, cluster__number=0, cluster__country__number=0)
        self.summary = histograms_factories.SummaryFactory(station=self.station)
        self.data = histograms_factories.DailyHistogramFactory(source=self.summary, type__slug='eventtime')
        self.config = histograms_factories.ConfigurationFactory(source=self.summary)
        super(TestViews, self).setUp()

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

    def test_station_redirect_to_latest(self):
        kwargs = {'station_number': self.station.number}
        response = self.client.get(reverse('status:station:data', kwargs=kwargs))
        self.assertEqual(302, response.status_code)
        kwargs = {'station_number': self.station.number}
        kwargs.update(date_as_kwargs(self.summary.date))
        self.assertEqual(reverse('status:station:data', kwargs=kwargs), response['Location'])

    def test_stations_data(self):
        kwargs = {'station_number': self.station.number}
        kwargs.update(date_as_kwargs(self.summary.date))
        self.get_html(reverse('status:station:data', kwargs=kwargs))

    def test_stations_data_invalid_date(self):
        kwargs = {'station_number': self.station.number}
        kwargs.update(date_as_kwargs(self.summary.date))
        kwargs['month'] = 13
        response = self.client.get(reverse('status:station:data', kwargs=kwargs))
        self.assertEqual(404, response.status_code)

    def test_help(self):
        self.get_html(reverse('status:help'))


class TestSourceViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.station = StationFactory(number=1, cluster__number=0, cluster__country__number=0)
        self.summary = histograms_factories.SummaryFactory(station=self.station)
        self.network_summary = histograms_factories.NetworkSummaryFactory(date=self.summary.date)
        super(TestSourceViews, self).setUp()

    def get_tsv(self, url):
        """Get url and check if the response is OK and valid TSV"""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/tab-separated-values', response['Content-Type'])

        # Expect properly formatted TSV
        genfromtxt(StringIO(response), delimiter='\t', dtype=None)

        return response

    def test_network_histograms(self):
        for network_histogram_type in ['coincidencetime', 'coincidencenumber']:
            histograms_factories.NetworkHistogramFactory(source=self.network_summary, type__slug=network_histogram_type)
            kwargs = date_as_kwargs(self.network_summary.date)
            self.get_tsv(reverse('status:source:{type}'.format(type=network_histogram_type), kwargs=kwargs))

    def test_daily_histograms(self):
        kwargs = {'station_number': self.station.number}
        kwargs.update(date_as_kwargs(self.summary.date))

        for daily_histogram_type in ['eventtime', 'zenith', 'azimuth']:
            histograms_factories.DailyHistogramFactory(source=self.summary, type__slug=daily_histogram_type)
            self.get_tsv(reverse('status:source:{type}'.format(type=daily_histogram_type), kwargs=kwargs))

        for daily_histogram_type in ['pulseheight', 'pulseintegral', 'singleslow', 'singleshigh']:
            histograms_factories.MultiDailyHistogramFactory(source=self.summary, type__slug=daily_histogram_type)
            self.get_tsv(reverse('status:source:{type}'.format(type=daily_histogram_type), kwargs=kwargs))

        # Get full eventtime data for the station
        kwargs = {'station_number': self.station.number}
        self.get_tsv(reverse('status:source:eventtime', kwargs=kwargs))

    def test_daily_datasets(self):
        kwargs = {'station_number': self.station.number}
        kwargs.update(date_as_kwargs(self.summary.date))

        for daily_dataset_type in ['barometer', 'temperature']:
            histograms_factories.DailyDatasetFactory(source=self.summary, type__slug=daily_dataset_type)
            self.get_tsv(reverse('status:source:{type}'.format(type=daily_dataset_type), kwargs=kwargs))

        for daily_dataset_type in ['singlesratelow', 'singlesratehigh']:
            histograms_factories.MultiDailyDatasetFactory(source=self.summary, type__slug=daily_dataset_type)
            self.get_tsv(reverse('status:source:{type}'.format(type=daily_dataset_type), kwargs=kwargs))

    def test_configs(self):
        kwargs = {'station_number': self.station.number}
        histograms_factories.ConfigurationFactory(source=self.summary)

        for config_type in ['electronics', 'voltage', 'current', 'gps', 'trigger']:
            self.get_tsv(reverse('status:source:{type}'.format(type=config_type), kwargs=kwargs))

    def test_station_layout(self):
        kwargs = {'station_number': self.station.number}
        StationLayoutFactory(station=self.station)
        self.get_tsv(reverse('status:source:layout', kwargs=kwargs))

    def test_detector_offsets(self):
        kwargs = {'station_number': self.station.number}
        histograms_factories.DetectorTimingOffsetFactory(source=self.summary)
        self.get_tsv(reverse('status:source:detector_offsets', kwargs=kwargs))

    def test_station_offsets(self):
        other_station = StationFactory(number=2, cluster__number=0, cluster__country__number=0)
        ref_summary = histograms_factories.SummaryFactory(station=other_station)
        histograms_factories.StationTimingOffsetFactory(ref_source=ref_summary, source=self.summary)

        if other_station.number < self.station.number:
            kwargs = {
                'ref_station_number': other_station.number,
                'station_number': self.station.number
            }
        else:
            kwargs = {
                'ref_station_number': self.station.number,
                'station_number': other_station.number
            }

        self.get_tsv(reverse('status:source:station_offsets', kwargs=kwargs))
