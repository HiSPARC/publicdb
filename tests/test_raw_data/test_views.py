import datetime

from os.path import dirname, join

from django.test import TestCase, override_settings
from django.urls import reverse

from ..factories import histograms_factories, inforecords_factories


@override_settings(ESD_PATH=join(dirname(__file__), '../data/esd'))
class TestDownload(TestCase):

    def setUp(self):
        # Required models
        cluster = inforecords_factories.ClusterFactory(name='Amsterdam', number=0, country__number=0)
        self.station = inforecords_factories.StationFactory(name='Nikhef', number=501, cluster=cluster)
        self.summary = histograms_factories.SummaryFactory(
            station=self.station, date=datetime.date(2017, 1, 1),
            needs_update_events=False, num_events=168,
            needs_update_weather=False, num_weather=60,
            needs_update_config=False, num_config=1,
            needs_update_singles=False, num_singles=301,
            needs_update=False,
        )

    def assert_download_equal_to_reference_tsv(self, data_type):
        # Expected data
        reference_path = join(dirname(__file__), f'../data/tsv/{data_type}-s501-20170101.tsv')
        with open(reference_path) as reference_file:
            reference_tsv = reference_file.read()
        # Get actual data
        kwargs = {'station_number': self.station.number}
        url = reverse(f'data:{data_type}', kwargs=kwargs)
        response = self.client.get(url, {'start': self.summary.date.isoformat()})
        tsv = b''.join(response.streaming_content).decode('utf-8')
        self.assertEqual(reference_tsv.strip(), tsv.strip())

    def test_download_events(self):
        self.assert_download_equal_to_reference_tsv('events')

    def test_download_weather(self):
        self.assert_download_equal_to_reference_tsv('weather')

    def test_download_singles(self):
        self.assert_download_equal_to_reference_tsv('singles')
