import datetime
import time
import os
import sys
import code
import logging
import unittest

import tables
import numpy

from mock import patch

from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings

from lib.test import datastore as test_datastore
from . import datastore, jobs, esd, fit_pulseheight_peak
from .models import *


histograms_logger = logging.getLogger('histograms')
histograms_logger.setLevel(logging.INFO)

DATE1 = datetime.date(2011, 7, 7)
DATE2 = datetime.date(2012, 5, 16)
DATETEST = datetime.date(2013, 11, 4)
STATION1 = 501
STATION2 = 502
STATIONTEST = 99


class BaseHistogramsTestCase(TransactionTestCase):

    fixtures = ['tests_inforecords']

    def setUp(self):

        # make progressbar(list) do nothing (i.e., return list)
        self.progressbar_patcher = patch('progressbar.ProgressBar')
        self.progressbar_mock = self.progressbar_patcher.start()
        self.progressbar_mock.return_value.side_effect = lambda x: x

        # Setup test datastore

        # The tests require a data file. We will download some data and
        # put it in a test directory. It needs to be writable by the
        # user who initiates the tests.

        self.original_datastore_path = settings.DATASTORE_PATH
        self.original_esd_path = settings.ESD_PATH
        path = os.path.join(settings.TEST_DATASTORE_PATH, "histograms")
        test_datastore.setup_test_datastore_directory(path)

        # Download data

        # Download real data of station 501 and 502 on 7 July 2011
        # Here is data where we can fit the pulseheight MPV,
        # and we get two stations to find coincidences.

        date = DATE1
        file = test_datastore.get_datafile_path(date)

        if not os.path.exists(file):
            test_datastore.download_data_station(STATION1, date, get_blobs=True)
            test_datastore.download_data_station(STATION2, date, get_blobs=True)

        self.assertTrue(os.path.exists(file))

        try:
            data = tables.open_file(file, "r")
        except Exception:
            self.fail()

        self.assertEqual(data.root.hisparc.cluster_amsterdam.station_501.events.nrows, 63322)
        self.assertEqual(data.root.hisparc.cluster_amsterdam.station_501.weather.nrows, 26317)
        self.assertEqual(data.root.hisparc.cluster_amsterdam.station_502.events.nrows, 55967)

        data.close()

        # Download real data of station 501 on 16 May 2012, which also
        # include weather data and configuration update.

        date = DATE2
        file = test_datastore.get_datafile_path(date)

        if not os.path.exists(file):
            test_datastore.download_data_station(STATION1, date, get_blobs=True)

        self.assertTrue(os.path.exists(file))

        try:
            data = tables.open_file(file, "r")
        except Exception:
            self.fail()

        self.assertEqual(data.root.hisparc.cluster_amsterdam.station_501.events.nrows, 6843)
        self.assertEqual(data.root.hisparc.cluster_amsterdam.station_501.weather.nrows, 25918)
        self.assertEqual(data.root.hisparc.cluster_amsterdam.station_501.config.nrows, 1)

        data.close()

        # Download test data of station 99 on 4 November 2013.
        # This contains 2 events and a configuration from this test station.

        date = DATETEST
        file = test_datastore.get_datafile_path(date)

        if not os.path.exists(file):
            test_datastore.download_data_station(STATIONTEST, date, get_blobs=True)

        self.assertTrue(os.path.exists(file))

        try:
            data = tables.open_file(file, "r")
        except Exception:
            self.fail()

        self.assertEqual(data.root.hisparc.cluster_amsterdam.station_99.events.nrows, 2)
        self.assertEqual(data.root.hisparc.cluster_amsterdam.station_99.config.nrows, 1)

        data.close()

        # Reset last updated state

        # Reset generator state such that it will always update when new
        # files are found.

        state = GeneratorState.objects.get()
        state.update_last_run = datetime.datetime.fromtimestamp(0)
        state.check_last_run = datetime.datetime.fromtimestamp(0)
        state.save()

        super(BaseHistogramsTestCase, self).setUp()

    def tearDown(self):
        super(BaseHistogramsTestCase, self).tearDown()

        settings.DATASTORE_PATH = self.original_datastore_path
        settings.ESD_PATH = self.original_esd_path

    #def test_interactive_shell(self):
    #    code.interact(local=dict(globals(), **locals()))


class DatastoreTestCase(BaseHistogramsTestCase):

    def setUp(self):
        super(DatastoreTestCase, self).setUp()

    def tearDown(self):
        super(DatastoreTestCase, self).tearDown()

    def test_datastore_check_for_new_events(self):
        """ Check for new events when the timestamp is 0.

        Since this corresponds to 1 January 1970, this should return at
        least 1 result.

        """
        last_check_time = time.mktime(datetime.date.fromtimestamp(0).timetuple())

        event_summary = datastore.check_for_new_events(last_check_time)

        self.assertTrue(len(event_summary))

    def test_datastore_check_for_new_events_at_the_end_of_epoch(self):
        """ Check for new events when the timestamp is 2**31 - 1.

        Since this corresponds to 19 January 2038, this should return
        zero results, unless we are in or past the year 2038.

        """
        last_check_time = 2**31 - 1.0

        event_summary = datastore.check_for_new_events(last_check_time)

        self.assertEqual(len(event_summary), 0)


class CheckForUpdatesTestCase(BaseHistogramsTestCase):

    def setUp(self):
        super(CheckForUpdatesTestCase, self).setUp()

    def tearDown(self):
        super(CheckForUpdatesTestCase, self).tearDown()

    def test_jobs_check_for_updates(self):
        """ Cross-checks the number of Summaries given by the datastore function
            with the number of Summaries in the database after calling
            jobs.check_for_updates()
        """

        self.assertTrue(jobs.check_for_updates())

        last_check_time = time.mktime(datetime.date.fromtimestamp(0).timetuple())
        event_summary = datastore.check_for_new_events(last_check_time)

        self.assertTrue(len(event_summary))

        # Cross-check event_summary with the database Summary

        count_need_updates = 0
        for date, station_list in event_summary.iteritems():
            for station, table_list in station_list.iteritems():
                if len(table_list) > 0:
                    count_need_updates += 1

        summaries_need_update = Summary.objects.filter(needs_update=True).count()

        # code.interact(local=dict(globals(), **locals()))

        self.assertEqual(count_need_updates, summaries_need_update)

    def test_jobs_check_for_updates_while_check_is_running(self):
        """ When an check_for_updates() is already running, a second call
            to check_for_updates() should return False.
        """

        state = GeneratorState.objects.get()
        state.check_is_running = True
        state.save()

        self.assertFalse(jobs.check_for_updates())

    def test_jobs_check_for_updates_at_the_end_of_epoch(self):
        """ Check for updates when the timestamp is 2**31 - 1. No summaries
            should be set to be updated. Unless we are past 2038..
        """

        state = GeneratorState.objects.get()
        state.check_last_run = datetime.datetime.fromtimestamp(2**31-1)
        state.save()

        self.assertTrue(jobs.check_for_updates())

        summaries_need_update = Summary.objects.filter(needs_update=True).count()

        self.assertEqual(summaries_need_update, 0)


class JobsPulseheightFitTestCase(BaseHistogramsTestCase):

    fixtures = ['tests_inforecords', 'tests_histograms']

    def setUp(self):

        # Contents
        # 1. Initialize work space
        # 2. Make sure there is an ESD (event summary data) file

        # 1. Initialize work space
        # Download data files
        # Empty all fits (there should be none beforehand)

        # Download data files and setup the test datastore
        super(JobsPulseheightFitTestCase, self).setUp()

        # Empty all fits
        PulseheightFit.objects.all().delete()

        # 2. Make sure there is an ESD (event summary data) file
        if os.path.exists(esd.get_esd_data_path(DATE1)):
            return

        # If it doesn't exist yet, generate the ESD file. This is done in
        # two steps. First jobs.check_for_updates(), this sets the flag
        # "needs_update" to true. Second, jobs.update_esd() will update or
        # create the ESD file when it sees the "needs_update".

        # jobs.check_for_updates

        Summary.objects.filter(date__gte=DATE1).delete()

        self.assertTrue(jobs.check_for_updates())

        # jobs.update_esd

        summary = Summary.objects.get(station__number=STATION1, date=DATE1)

        self.assertTrue(summary.needs_update)

        jobs.update_esd()

    def tearDown(self):
        super(JobsPulseheightFitTestCase, self).tearDown()

    def test_jobs_update_pulseheight_fit_normal(self):
        """Try pulseheight fit on good data with available configuration.

        With everything ok there should be 4 (number of detectors) fits
        in the database.

        """
        summary = Summary.objects.get(station__number=STATION1, date=DATE1)

        # Try to fit data
        jobs.update_pulseheight_fit(summary)

        # Validate output, four fits are expected
        fits = PulseheightFit.objects.all().count()
        self.assertEqual(fits, 4)

    def test_jobs_update_pulseheight_fit_no_config(self):
        """ When there is no config, no fit should have been made"""

        # Delete all configurations
        Configuration.objects.all().delete()

        summary = Summary.objects.get(station__number=STATION1, date=DATE1)

        # Try to fit data, although there is no configuration.
        # Configuration data contains info on the number of detectors.
        # If no config data is found, nothing should be done.
        jobs.update_pulseheight_fit(summary)

        # Validate output, no fits are expected
        fits = PulseheightFit.objects.all().count()
        self.assertEqual(fits, 0)

    def test_jobs_save_pulseheight_fit_normal(self):
        """ Saving a PulseheightFit in normal conditions"""

        summary = Summary.objects.get(station__number=STATION1, date=DATE1)

        # Create and save fits
        fits = [PulseheightFit(source=summary, plate=detector_n,
                               initial_mpv=1, initial_width=2,
                               fitted_mpv=3, fitted_mpv_error=4,
                               fitted_width=5, fitted_width_error=6,
                               chi_square_reduced=7)
                for detector_n in [1, 2, 3, 4]]

        jobs.save_pulseheight_fits(summary, fits)

        # Validate output
        fits = PulseheightFit.objects.filter(source=summary)
        self.assertEqual(len(fits), 4)
        self.assertEqual(fits[0].initial_mpv, 1.0)

    def test_jobs_save_pulseheight_fit_no_fits(self):
        """ Saving no fits should do nothing

        The second argument of save_pulseheight_fits is expected to be a list
        of histograms.models.PulseheightFit. Instead we pass it an empty list
        denoting no fit results. No fits in the database are expected.

        """
        summary = Summary.objects.get(station__number=STATION1, date=DATE1)

        jobs.save_pulseheight_fits(summary, [])

        fits = PulseheightFit.objects.all().count()
        self.assertEqual(fits, 0)

    def test_jobs_save_pulseheight_fit_update(self):
        """ Updating a PulseheightFit should be reflected in the database

        Try to update an existing fit. What matters is that the source and
        detector are the same, as the pair is defined to be unique in the table.

        """
        summary = Summary.objects.get(station__number=STATION1, date=DATE1)

        detector_n = 1

        fit = PulseheightFit(source=summary, plate=detector_n,
                             initial_mpv=1, initial_width=2,
                             fitted_mpv=3, fitted_mpv_error=4,
                             fitted_width=5, fitted_width_error=6,
                             chi_square_reduced=7)

        fit.save()

        fits = PulseheightFit.objects.filter(source=summary)
        self.assertEqual(len(fits), 1)

        fits[0].initial_mpv = 10

        jobs.save_pulseheight_fits(summary, fits)

        fits = PulseheightFit.objects.filter(source=summary)
        self.assertEqual(len(fits), 1)
        self.assertEqual(fits[0].initial_mpv, 10.0)


class CoincidencesESDCase(BaseHistogramsTestCase):

    fixtures = ['tests_inforecords', 'tests_histograms']

    def setUp(self):
        # Download data files and setup the test datastore
        super(CoincidencesESDCase, self).setUp()

        # Make sure the ESD (event summary data) files exist
        for date, stations in [(DATE1, (STATION1, STATION2)),
                               (DATE2, (STATION1,)),
                               (DATETEST, (STATIONTEST,))]:
            if not os.path.exists(esd.get_esd_data_path(date)):
                for station in stations:
                    jobs.process_possible_tables_for_station(
                            station, {'events': 1}, date)
                    summary = Summary.objects.get(station__number=station,
                                                  date=date)
                    self.assertTrue(summary.needs_update)
                jobs.update_esd()

        # Make sure coincidences are analysed
        for date in [DATE1, DATE2, DATETEST]:
            with tables.open_file(esd.get_esd_data_path(date), "r") as data:
                try:
                    data.get_node('/', 'coincidences')
                    NetworkSummary.objects.get_or_create(date=date)
                except tables.NoSuchNodeError:
                    jobs.process_possible_tables_for_network(date, 'events')
        jobs.update_coincidences()

    def tearDown(self):
        super(CoincidencesESDCase, self).tearDown()

    def test_create_network_summary(self):
        """Create or update Network Summary

        Test that updates have run and the jobs correctly creates the
        Network Summaries and sets the flags.

        """
        for date in [DATE1, DATE2, DATETEST]:
            network_summary = NetworkSummary.objects.get(date=date)
            self.assertFalse(network_summary.needs_update)
            self.assertFalse(network_summary.needs_update_coincidences)

        NetworkSummary.objects.all().delete()
        self.assertRaises(NetworkSummary.DoesNotExist, NetworkSummary.objects.get, date=DATE1)

        for date in [DATE1, DATE2, DATETEST]:
            jobs.process_possible_tables_for_network(date, 'events')
            network_summary = NetworkSummary.objects.get(date=date)
            self.assertTrue(network_summary.needs_update)
            self.assertTrue(network_summary.needs_update_coincidences)

    def base_coincidences_for_date(self, date, n_coincidences, n_stations):
        """Check number of entries in coincidence tables for a date

        Check the number of coincidences, check that this matches to the
        number of c_indexes. Also check the number of participating
        stations.

        """
        file = test_datastore.get_esd_datafile_path(date)
        data = tables.open_file(file, "r")
        self.assertEqual(data.root.coincidences.coincidences.nrows,
                         n_coincidences)
        self.assertEqual(data.root.coincidences.c_index.nrows,
                         data.root.coincidences.coincidences.nrows)
        self.assertEqual(data.root.coincidences.s_index.nrows, n_stations)
        data.close()

    def test_coincidences_DATE1(self):
        """Check number of entries in coincidence tables for DATE1

        Some coincidences will be found, the station index should contain
        the references to the two stations.

        """
        self.base_coincidences_for_date(DATE1, 1968, 2)

    def test_coincidences_DATE2(self):
        """Check for zero coincidences for DATE2

        So no coincidences should be found, the coincidences table should
        still be created, but empty. The station index should contain
        a reference to the one station.

        """
        self.base_coincidences_for_date(DATE2, 0, 1)

    def test_coincidences_DATETEST(self):
        """Check for zero coincidences for DATETEST

        No coincidences should be found, the coincidences tables should
        still be created, but empty.

        """
        self.base_coincidences_for_date(DATETEST, 0, 0)


class UpdateAllHistogramsTestCase(BaseHistogramsTestCase):

    fixtures = ['tests_inforecords', 'tests_histograms']

    def setUp(self):
        # Download data files and setup the test datastore
        super(UpdateAllHistogramsTestCase, self).setUp()

        DailyHistogram.objects.all().delete()
        DailyDataset.objects.all().delete()
        PulseheightFit.objects.all().delete()
        self.redirect_stdout_stderr_to_devnull()

    def tearDown(self):
        self.restore_stdout_stderr()
        super(UpdateAllHistogramsTestCase, self).tearDown()

    def test_jobs_update_all_histograms_while_update_is_running(self):
        """Only one update_all_histograms at a time

        When an update_all_histograms() is already running, a second
        call to update_all_histograms() should return False.

        """
        state = GeneratorState.objects.get()
        state.update_is_running = True
        state.save()

        self.assertFalse(jobs.update_all_histograms())

    def base_test_jobs_update_all_histograms_501_date(self, date):
        """Tests jobs.update_all_histograms() by processing a single Summary.

        Also checks if event histograms are created.

        :param date: Date for which to update the histograms of STATION1.

        :return: Summary object for which the histograms are processed.

        """
        # Prepare database
        Summary.objects.filter(date__gte=date).delete()

        # Set the needs_update_x fields
        self.assertTrue(jobs.check_for_updates())

        # Update only one station
        #
        # Pick one summary, set all other summaries such that they don't
        # need to be updated.
        test_summary = Summary.objects.get(station__number=STATION1, date=date)
        summaries = Summary.objects.exclude(id=test_summary.id)

        for summary in summaries:
            summary.needs_update = False
            summary.needs_update_events = False
            summary.needs_update_config = False
            summary.needs_update_weather = False
            summary.save()

        # Run updates for that one station

        self.assertTrue(jobs.update_all_histograms())

        state = GeneratorState.objects.get()
        self.assertEqual(state.update_is_running, False)

        self.assertEqual(Summary.objects.filter(needs_update=True).count(), 0)

        # Validate output

        # Check for pulseheight, pulseintegral and eventtime histograms.
        # There should be three entries in the DailyHistogram table.

        histograms = DailyHistogram.objects.filter(
                source__station__number=STATION1, source__date=date)
        self.assertEqual(len(histograms), 3)

        for h in histograms:
            self.assertEqual(h.source, test_summary)

        return test_summary

    def base_test_jobs_update_all_histograms_501_DATE1(self):
        """Tests jobs.update_all_histograms() by processing a single Summary.

        It then checks for the output in the database. The data of
        station 501 on 2011/7/7 contains events data that is suitable
        for fitting the pulseheight mpv.

        """
        test_summary = self.base_test_jobs_update_all_histograms_501_date(DATE1)

        # Check for pulseheight mpv fit

        fits = PulseheightFit.objects.all()
        self.assertEqual(len(fits), 4)

        self.assertTrue(222 < fits[0].fitted_mpv < 226)
        self.assertTrue(220 < fits[1].fitted_mpv < 224)
        self.assertTrue(240 < fits[2].fitted_mpv < 244)
        self.assertTrue(231 < fits[3].fitted_mpv < 235)

        # Check for temperature and barometer datasets
        # There should be two entries in the DailyDataset table.

        datasets = DailyDataset.objects.filter(
                source__station__number=STATION1, source__date=DATE1)

        self.assertEqual(len(datasets), 2)

        for d in datasets:
            self.assertEqual(d.source, test_summary)

    def base_test_jobs_update_all_histograms_501_DATE2(self):
        """Tests jobs.update_all_histograms() by processing a single Summary.

        It then checks for the output in the database. The data of
        station 501 on 2012/5/16 contains events, configuration and
        weather data, but the events data does not contain sufficient
        events to do a fit.

        """
        test_summary = self.base_test_jobs_update_all_histograms_501_date(DATE2)

        # Check for config

        config = Configuration.objects.filter(
                source__station__number=STATION1, source__date=DATE2)

        self.assertEqual(len(config), 1)
        self.assertEqual(config[0].source, test_summary)

        # Check for temperature and barometer datasets
        # There should be two entries in the DailyDataset table.

        datasets = DailyDataset.objects.filter(
                source__station__number=STATION1, source__date=DATE2)

        self.assertEqual(len(datasets), 2)

        for d in datasets:
            self.assertEqual(d.source, test_summary)

    @override_settings(USE_MULTIPROCESSING=False)
    def test_jobs_update_all_histograms_501_DATE1_single_threaded(self):
        """Single threaded histograms for station 501 on 2011/7/7"""
        self.base_test_jobs_update_all_histograms_501_DATE1()

    @unittest.skipIf('mysql' in settings.DATABASES['default']['ENGINE'],
                     "MySQL and multiprocessing don't seem to go well together"
                     ", test passes, but then hangs indefinitely.")
    @override_settings(USE_MULTIPROCESSING=True)
    def test_jobs_update_all_histograms_501_DATE1_multi_threaded(self):
        """Multi threaded histograms for station 501 on 2011/7/7"""
        self.base_test_jobs_update_all_histograms_501_DATE1()

    @override_settings(USE_MULTIPROCESSING=False)
    def test_jobs_update_all_histograms_501_DATE2_single_threaded(self):
        """Single threaded histograms for station 501 on 2012/5/16"""
        self.base_test_jobs_update_all_histograms_501_DATE2()

    @unittest.skipIf('mysql' in settings.DATABASES['default']['ENGINE'],
                     "MySQL and multiprocessing don't seem to go well together"
                     ", test passes, but then hangs indefinitely.")
    @override_settings(USE_MULTIPROCESSING=True)
    def test_jobs_update_all_histograms_501_DATE2_multi_threaded(self):
        """Multi threaded histograms for station 501 on 2012/5/16"""
        self.base_test_jobs_update_all_histograms_501_DATE2()

    def redirect_stdout_stderr_to_devnull(self):
        self.__stdout = sys.stdout
        self.__stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def restore_stdout_stderr(self):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self.__stdout
        sys.stderr = self.__stderr


class PulseheightFitErrorsTestCase(TestCase):

    def test_empty_data(self):
        fit = PulseheightFit()

        fit.error_message = ""
        self.assertEqual(len(fit.error_message), 0)

        data = numpy.zeros(100)
        fit = fit_pulseheight_peak.fit_pulseheight_peak(data)
        self.assertTrue(fit.error_message.count("Sum"))

    def test_data_low_average(self):
        fit = PulseheightFit()

        fit.error_message = ""
        self.assertEqual(len(fit.error_message), 0)

        data = numpy.random.normal(50, 5, 500)
        fit = fit_pulseheight_peak.fit_pulseheight_peak(data)
        self.assertTrue(fit.error_message.count("Average"))
