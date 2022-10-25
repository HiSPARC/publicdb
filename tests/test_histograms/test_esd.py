import datetime

from os.path import dirname, join

from django.test import TestCase, override_settings

from publicdb.histograms import esd

from ..factories import histograms_factories, inforecords_factories


@override_settings(ESD_PATH=join(dirname(__file__), '../data/esd'))
class TestESD(TestCase):

    def setup_station(self):
        cluster = inforecords_factories.ClusterFactory(name='Amsterdam', number=0, country__number=0)
        self.station = inforecords_factories.StationFactory(number=501, cluster=cluster)
        self.summary = histograms_factories.SummaryFactory(
            station=self.station, date=datetime.date(2017, 1, 1),
            needs_update_events=False, num_events=168,
            needs_update_weather=False, num_weather=60,
            needs_update_config=False, num_config=1,
            needs_update_singles=False, num_singles=301,
            needs_update=False,
        )

    def test_get_station_node_path(self):
        self.setup_station()
        self.assertEqual('/hisparc/cluster_amsterdam/station_501', esd.get_station_node_path(self.station))

    @override_settings(ESD_PATH='/foo/')
    def test_get_esd_data_path(self):
        self.assertEqual('/foo/2017/1/2017_1_1.h5', esd.get_esd_data_path(datetime.date(2017, 1, 1)))

    def test_get_event_timestamps(self):
        self.setup_station()
        timestamps = esd.get_event_timestamps(self.summary)
        self.assertEqual(168, len(timestamps))
        self.assertEqual(sorted(timestamps), list(timestamps))
        self.assertEqual(1483228806, timestamps[0])
        self.assertEqual(1483229100, timestamps[-1])
