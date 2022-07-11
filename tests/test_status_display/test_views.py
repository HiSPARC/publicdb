from io import BytesIO

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
        histograms_factories.EventtimeHistogramFactory(summary=self.summary)
        histograms_factories.ConfigurationFactory(summary=self.summary)
        super().setUp()

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
        response = self.client.get(reverse('status:station:summary', kwargs=kwargs))
        self.assertEqual(302, response.status_code)
        kwargs = {'station_number': self.station.number}
        kwargs.update(date_as_kwargs(self.summary.date))
        self.assertEqual(reverse('status:station:summary', kwargs=kwargs), response['Location'])

    def test_stations_data(self):
        kwargs = {'station_number': self.station.number}
        kwargs.update(date_as_kwargs(self.summary.date))
        self.get_html(reverse('status:station:summary', kwargs=kwargs))

    def test_stations_data_invalid_date(self):
        kwargs = {'station_number': self.station.number}
        kwargs.update(date_as_kwargs(self.summary.date))
        kwargs['month'] = 13
        response = self.client.get(reverse('status:station:summary', kwargs=kwargs))
        self.assertEqual(404, response.status_code)

    def test_help(self):
        self.get_html(reverse('status:help'))


class TestSourceViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.station = StationFactory(number=1, cluster__number=0, cluster__country__number=0)
        self.summary = histograms_factories.SummaryFactory(station=self.station)
        self.network_summary = histograms_factories.NetworkSummaryFactory(date=self.summary.date)
        super().setUp()

    def get_tsv(self, url):
        """Get url and check if the response is OK and valid TSV"""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/tab-separated-values', response['Content-Type'])

        # Expect properly formatted TSV
        genfromtxt(BytesIO(response.content), delimiter='\t', dtype=None)

        return response

    def assert_context_contains(self, expected_context, context):
        for key, value in expected_context.items():
            self.assertEqual(value, context[key])

    def test_network_histograms(self):
        factories = [
            histograms_factories.CoincidencetimeHistogramFactory,
            histograms_factories.CoincidencenumberHistogramFactory
        ]
        for factory in factories:
            data = factory(network_summary=self.network_summary)
            response = self.get_tsv(data.get_absolute_url())
            expected_context = {
                'data': list(zip(data.bins, data.values)),
                'date': self.network_summary.date.strftime('%-Y-%-m-%-d'),
            }
            self.assert_context_contains(expected_context, response.context)

    def test_daily_histograms(self):
        factories = [
            histograms_factories.EventtimeHistogramFactory,
            histograms_factories.AzimuthHistogramFactory,
            histograms_factories.ZenithHistogramFactory
        ]
        for factory in factories:
            data = factory(summary=self.summary)
            response = self.get_tsv(data.get_absolute_url())
            expected_context = {
                'data': list(zip(data.bins, data.values)),
                'date': self.summary.date.strftime('%-Y-%-m-%-d'),
                'station_number': str(self.station.number)
            }
            self.assert_context_contains(expected_context, response.context)

    def test_multi_daily_histograms(self):
        factories = [
            histograms_factories.PulseintegralHistogramFactory,
            histograms_factories.PulseheightHistogramFactory,
            histograms_factories.SingleslowHistogramFactory,
            histograms_factories.SingleshighHistogramFactory
        ]
        for factory in factories:
            data = factory(summary=self.summary)
            response = self.get_tsv(data.get_absolute_url())
            expected_context = {
                'data': list(zip(data.bins, *data.values)),
                'date': self.summary.date.strftime('%-Y-%-m-%-d'),
                'station_number': str(self.station.number)
            }
            self.assert_context_contains(expected_context, response.context)

    def test_full_eventtime_data(self):
        histograms_factories.EventtimeHistogramFactory(summary=self.summary)
        kwargs = {'station_number': self.station.number}
        self.get_tsv(reverse('status:source:eventtime', kwargs=kwargs))

    def test_daily_datasets(self):
        factories = [
            histograms_factories.BarometerDatasetFactory,
            histograms_factories.TemperatureDatasetFactory,
        ]
        for factory in factories:
            data = factory(summary=self.summary)
            response = self.get_tsv(data.get_absolute_url())
            expected_context = {
                'data': list(zip(data.x, data.y)),
                'date': self.summary.date.strftime('%-Y-%-m-%-d'),
                'station_number': str(self.station.number)
            }
            self.assert_context_contains(expected_context, response.context)

    def test_multi_daily_datasets(self):
        factories = [
            histograms_factories.SinglesratelowDatasetFactory,
            histograms_factories.SinglesratehighDatasetFactory,
        ]
        for factory in factories:
            data = factory(summary=self.summary)
            response = self.get_tsv(data.get_absolute_url())
            expected_context = {
                'data': list(zip(data.x, *data.y)),
                'date': self.summary.date.strftime('%-Y-%-m-%-d'),
                'station_number': str(self.station.number)
            }
            self.assert_context_contains(expected_context, response.context)

    def test_configs(self):
        kwargs = {'station_number': self.station.number}
        histograms_factories.ConfigurationFactory(summary=self.summary)

        for config_type in ['electronics', 'voltage', 'current', 'gps', 'trigger']:
            response = self.get_tsv(reverse(f'status:source:{config_type}', kwargs=kwargs))
            expected_context = {
                'station_number': str(self.station.number)
                # data structures are a bit more work to check.
            }
            self.assert_context_contains(expected_context, response.context)

    def test_station_layout(self):
        kwargs = {'station_number': self.station.number}
        StationLayoutFactory(station=self.station)
        self.get_tsv(reverse('status:source:layout', kwargs=kwargs))

    def test_detector_offsets(self):
        kwargs = {'station_number': self.station.number}
        histograms_factories.DetectorTimingOffsetFactory(summary=self.summary)
        self.get_tsv(reverse('status:source:detector_offsets', kwargs=kwargs))

    def test_station_offsets(self):
        other_station = StationFactory(number=2, cluster__number=0, cluster__country__number=0)
        ref_summary = histograms_factories.SummaryFactory(station=other_station)
        histograms_factories.StationTimingOffsetFactory(ref_summary=ref_summary, summary=self.summary)

        kwargs = {
            'ref_station_number': min(other_station.number, self.station.number),
            'station_number': max(other_station.number, self.station.number)
        }

        self.get_tsv(reverse('status:source:station_offsets', kwargs=kwargs))
