from datetime import date, datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from publicdb.histograms import models

from ..factories import histograms_factories, inforecords_factories


class TestNetworkSummary(TestCase):
    def setUp(self):
        self.batch_size = 5
        histograms_factories.NetworkSummaryFactory.create_batch(size=self.batch_size)

    def test_str(self):
        network_summary = histograms_factories.NetworkSummaryFactory(date=date(2016, 1, 12))
        self.assertEqual('Network Summary: 2016-01-12', str(network_summary))

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
        self.assertEqual('Summary: 9 - 2016-01-12', str(summary))

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


class TestConfiguration(TestCase):
    def setUp(self):
        self.station = inforecords_factories.StationFactory(number=9, cluster__number=0, cluster__country__number=0)
        self.summary = histograms_factories.SummaryFactory(station=self.station, date=date(2016, 1, 12))
        self.configuration = histograms_factories.ConfigurationFactory(
            summary=self.summary, timestamp=datetime.combine(self.summary.date, time(10, 11, 20))
        )

    def test_str(self):
        self.assertEqual('9 - 2016-01-12 10:11:20', str(self.configuration))

    def test_station(self):
        self.assertEqual(9, self.configuration.station())

    def test_master(self):
        master_version = int(self.configuration.mas_version.split(' ')[1])
        self.assertEqual(master_version, self.configuration.master)
        self.assertEqual(self.configuration._master(), self.configuration.master)

    def test_slave(self):
        slave_version = int(self.configuration.slv_version.split(' ')[1])
        self.assertEqual(slave_version, self.configuration.slave)
        self.assertEqual(self.configuration._slave(), self.configuration.slave)

    def test_master_fpga(self):
        master_fpga_version = int(self.configuration.mas_version.split(' ')[3])
        self.assertEqual(master_fpga_version, self.configuration.master_fpga)

    def test_slave_fpga(self):
        slave_fpga_version = int(self.configuration.slv_version.split(' ')[3])
        self.assertEqual(slave_fpga_version, self.configuration.slave_fpga)

    def test_extract_hardware_serial(self):
        self.assertEqual(123, self.configuration.extract_hardware_serial('Foo 123 Bar 456'))
        self.assertEqual(-1, self.configuration.extract_hardware_serial('Foo 0 Bar 456'))
        self.assertEqual(-1, self.configuration.extract_hardware_serial('Foo'))

    def test_extract_fpga_version(self):
        self.assertEqual(456, self.configuration.extract_fpga_version('Foo 123 Bar 456'))
        self.assertEqual(-1, self.configuration.extract_fpga_version('Foo 123 Bar 0'))
        self.assertEqual(-1, self.configuration.extract_fpga_version('Foo 123 Bar'))


class TestHistogramType(TestCase):
    def test_str(self):
        histogram_type = histograms_factories.HistogramTypeFactory.build()
        self.assertEqual(histogram_type.name, str(histogram_type))


class TestDatasetType(TestCase):
    def test_str(self):
        dataset_type = histograms_factories.DatasetTypeFactory.build()
        self.assertEqual(dataset_type.name, str(dataset_type))


class TestStationTimingOffset(TestCase):
    def setUp(self):
        self.ref_station = inforecords_factories.StationFactory(number=9, cluster__number=0, cluster__country__number=0)
        self.ref_summary = histograms_factories.SummaryFactory(station=self.ref_station, date=date(2016, 1, 12))
        self.ref_summary_date = histograms_factories.SummaryFactory(station=self.ref_station, date=date(2010, 2, 13))

        self.station = inforecords_factories.StationFactory(number=13, cluster__number=0, cluster__country__number=0)
        self.summary = histograms_factories.SummaryFactory(station=self.station, date=date(2016, 1, 12))
        self.summary_date = histograms_factories.SummaryFactory(station=self.station, date=date(2010, 2, 13))

    def test_clean(self):
        offset = histograms_factories.StationTimingOffsetFactory.build(
            ref_summary=self.ref_summary, summary=self.summary
        )
        offset.clean()

    def test_clean_same_station(self):
        offset = histograms_factories.StationTimingOffsetFactory.build(
            ref_summary=self.ref_summary, summary=self.ref_summary
        )
        with self.assertRaisesMessage(ValidationError, 'stations'):
            offset.clean()

        offset = histograms_factories.StationTimingOffsetFactory.build(
            ref_summary=self.ref_summary, summary=self.ref_summary_date
        )
        with self.assertRaisesMessage(ValidationError, 'stations'):
            offset.clean()

    def test_clean_different_date(self):
        offset = histograms_factories.StationTimingOffsetFactory.build(
            ref_summary=self.ref_summary, summary=self.summary_date
        )
        with self.assertRaisesMessage(ValidationError, 'summary dates'):
            offset.clean()
