import datetime

from django.test import TestCase

from publicdb.raw_data.forms import CoincidenceDownloadForm, DataDownloadForm

from ..factories import histograms_factories, inforecords_factories


class TestDataDownloadForm(TestCase):

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

    def test_clean_valid(self):
        valid_form_data = [
            {'data_type': 'events', 'station_events': self.station.id, 'start': '2017-1-1', 'end': '2017-1-2'},
            {'data_type': 'weather', 'station_weather': self.station.id, 'start': '2017-1-1', 'end': '2017-1-2'},
            {'data_type': 'singles', 'station_singles': self.station.id, 'start': '2017-1-1', 'end': '2017-1-2'},
            {'data_type': 'lightning', 'lightning_type': 0, 'start': '2014-10-1', 'end': '2014-11-4'},
        ]
        for data in valid_form_data:
            form = DataDownloadForm(data)
            self.assertTrue(form.is_valid(), msg=form.errors.as_json())

    def test_clean_invalid(self):
        invalid_form_data = [
            {'data_type': 'events', 'station_weather': self.station.id, 'start': '2017-1-1', 'end': '2017-1-2'},
            {'data_type': 'weather', 'station_events': self.station.id, 'start': '2017-1-1', 'end': '2017-1-2'},
            {'data_type': 'lightning', 'lightning_type': 10, 'start': '2014-10-1', 'end': '2014-11-4'},
            {'data_type': 'events', 'station_events': self.station.id},
        ]
        for data in invalid_form_data:
            form = DataDownloadForm(data)
            self.assertFalse(form.is_valid())


class TestCoincidenceDownloadForm(TestCase):

    def setUp(self):
        # Required models
        self.cluster = inforecords_factories.ClusterFactory(name='Amsterdam', number=0, country__number=0)
        self.station = inforecords_factories.StationFactory(name='Nikhef', number=501, cluster=self.cluster)
        self.station2 = inforecords_factories.StationFactory(name='Nikhef2', number=502, cluster=self.cluster)
        self.summary = histograms_factories.SummaryFactory(
            station=self.station, date=datetime.date(2017, 1, 1),
            needs_update_events=False, num_events=168,
            needs_update_weather=False, num_weather=60,
            needs_update_config=False, num_config=1,
            needs_update_singles=False, num_singles=301,
            needs_update=False,
        )

    def test_clean_valid(self):
        valid_form_data = [
            {'filter_by': 'network', 'start': '2017-1-1', 'end': '2017-1-2', 'n': 2},
            {'filter_by': 'stations', 'stations': '501,502', 'start': '2017-1-1', 'end': '2017-1-2', 'n': 2},
            {'filter_by': 'stations', 'stations': '[502, 501]', 'start': '2017-1-1', 'end': '2017-1-2', 'n': 2},
            {'filter_by': 'cluster', 'cluster': self.cluster.id, 'start': '2017-1-1', 'end': '2017-1-2', 'n': 2},
        ]
        for data in valid_form_data:
            form = CoincidenceDownloadForm(data)
            self.assertTrue(form.is_valid(), msg=form.errors.as_json())

    def test_clean_invalid(self):
        invalid_form_data = [
            ('cluster', 'invalid_choice', {'filter_by': 'cluster', 'start': '2017-1-1', 'end': '2017-1-2', 'n': 2}),
            ('stations', 'required', {'filter_by': 'stations', 'stations': '', 'start': '2017-1-1', 'end': '2017-1-2', 'n': 2}),
            ('stations', 'incorrect_entry', {'filter_by': 'stations', 'stations': '501;102', 'start': '2017-1-1', 'end': '2017-1-2', 'n': 2}),
            ('stations', 'too_few', {'filter_by': 'stations', 'stations': '501', 'start': '2017-1-1', 'end': '2017-1-2', 'n': 2}),
            ('stations', 'too_many', {'filter_by': 'stations', 'stations': (',501' * 32)[1:], 'start': '2017-1-1', 'end': '2017-1-2', 'n': 2}),
            ('stations', 'invalid_choices', {'filter_by': 'stations', 'stations': '501,501', 'start': '2017-1-1', 'end': '2017-1-2', 'n': 2}),
            ('stations', 'invalid_choices', {'filter_by': 'stations', 'stations': '501,100001', 'start': '2017-1-1', 'end': '2017-1-2', 'n': 2}),
        ]
        for field, error_code, data in invalid_form_data:
            form = CoincidenceDownloadForm(data)
            self.assertFalse(form.is_valid())
            self.assertTrue(form.has_error(field, error_code), msg=(field, error_code, data))
