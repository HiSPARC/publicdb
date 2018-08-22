from datetime import date, timedelta

from django.test import TestCase

from publicdb.histograms import models

from ..factories import histograms_factories, inforecords_factories


class TestNetworkSummary(TestCase):
    def setUp(self):
        self.batch_size = 5
        histograms_factories.NetworkSummaryFactory.create_batch(size=self.batch_size)

    def test_str(self):
        network_summary = histograms_factories.NetworkSummaryFactory(date=date(2016, 1, 12))
        self.assertEqual('Network Summary: 12 Jan 2016', str(network_summary))

    def test_get_absolute_url(self):
        network_summary = histograms_factories.NetworkSummaryFactory(date=date(2016, 1, 12))
        self.assertEqual('/show/network/coincidences/2016/1/12/', network_summary.get_absolute_url())

    def test_valid_date_manager(self):
        # invalid past dates
        histograms_factories.NetworkSummaryFactory(date=date(2002, 1, 1))
        histograms_factories.NetworkSummaryFactory(date=models.FIRSTDATE - timedelta(days=1))
        # invalid future dates
        histograms_factories.NetworkSummaryFactory(date=date(3000, 1, 1))
        histograms_factories.NetworkSummaryFactory(date=date.today() + timedelta(days=1))
        self.assertEqual(self.batch_size, models.NetworkSummary.objects.valid_date().count())

    def test_with_coincidences_manager(self):
        """Only summaries with coincidences and a valid date"""
        # no coincidences
        histograms_factories.NetworkSummaryFactory(num_coincidences=None)
        # invalid past date
        histograms_factories.NetworkSummaryFactory(date=date(2002, 1, 1))
        self.assertEqual(self.batch_size, models.NetworkSummary.objects.with_coincidences().count())


class TestSummary(TestCase):
    def setUp(self):
        self.batch_size = 5
        self.station = inforecords_factories.StationFactory(number=9, cluster__number=0, cluster__country__number=0)
        histograms_factories.SummaryFactory.create_batch(size=self.batch_size, station=self.station)

    def test_str(self):
        summary = histograms_factories.SummaryFactory(date=date(2016, 1, 12), station=self.station)
        self.assertEqual('Summary: 9 - 12 Jan 2016', str(summary))

    def test_get_absolute_url(self):
        summary = histograms_factories.SummaryFactory(date=date(2016, 1, 12), station=self.station)
        self.assertEqual('/show/stations/9/2016/1/12/', summary.get_absolute_url())

    def test_valid_date_manager(self):
        # invalid past dates
        histograms_factories.SummaryFactory(date=date(2002, 1, 1), station=self.station)
        histograms_factories.SummaryFactory(date=models.FIRSTDATE - timedelta(days=1), station=self.station)
        # invalid future dates
        histograms_factories.SummaryFactory(date=date(3000, 1, 1), station=self.station)
        histograms_factories.SummaryFactory(date=date.today() + timedelta(days=1), station=self.station)
        self.assertEqual(self.batch_size, models.Summary.objects.valid_date().count())

    def test_with_data_manager(self):
        """Only summaries with events or weather and a valid date"""
        # no events and weather
        histograms_factories.SummaryFactory(num_events=None, num_weather=None, station=self.station)
        # invalid past date
        histograms_factories.SummaryFactory(date=date(2002, 1, 1), station=self.station)
        self.assertEqual(self.batch_size, models.Summary.objects.with_data().count())

    def test_with_config_manager(self):
        """Only summaries with config and a valid date"""
        # no configs
        histograms_factories.SummaryFactory(num_config=None, station=self.station)
        # invalid past date
        histograms_factories.SummaryFactory(date=date(2002, 1, 1), station=self.station)
        self.assertEqual(self.batch_size, models.Summary.objects.with_config().count())
