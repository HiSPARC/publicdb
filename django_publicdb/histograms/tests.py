# Python
import datetime
import time
import string
import sys
import os

# Django
from django.conf import settings
from django.test import TestCase

# Publicdb
from django_publicdb.tests import datastore as tests_datastore
from django_publicdb.histograms import models, datastore, jobs

class MyHistogramsTests(TestCase):

    fixtures = [
        'tests_inforecords'
    ]

    #---------------------------------------------------------------------------
    # Setup and teardown
    #---------------------------------------------------------------------------

    def setUp(self):

        # The tests require a data file. We will download some data and put it
        # in a test directory. It needs to be writable by the user who initiates
        # the tests.

        self.original_datastore_path = settings.DATASTORE_PATH

        tests_datastore.setup_test_datastore_directory(os.path.join(
            settings.TEST_DATASTORE_PATH,
            "histograms"
        ))

        # Download real data of station 501 on 16 May 2012, which also
        # include weather data and configuration update.

        date = datetime.date(2012, 5, 16)

        file = tests_datastore.get_datafile_path(date)

        if not os.path.exists(file):
            tests_datastore.download_data_station(501, date, get_blobs=True)

        self.assertTrue(os.path.exists(file))

        #

        super(MyHistogramsTests, self).setUp()

    def tearDown(self):
        super(MyHistogramsTests, self).tearDown()

        settings.DATASTORE_PATH = self.original_datastore_path

    #---------------------------------------------------------------------------
    # Tests
    #---------------------------------------------------------------------------

    def test_datastore_check_for_new_events(self):
        """ Check for new events when the timestamp is 0. Since this corresponds
            to 1 January 1970, this should return at least 1 result.
        """

        last_check_time = time.mktime(datetime.date.fromtimestamp(0).timetuple())

        event_summary = datastore.check_for_new_events(last_check_time)

        self.assertTrue(len(event_summary) > 0)

    def test_datastore_check_for_new_events_at_the_end_of_epoch(self):
        """ Check for new events when the timestamp is 2**31 - 1. Since this
            corresponds to 1 January 1970, this should return zero results,
            unless we are in or past the year 2038.
        """

        last_check_time = 2**31 - 1.0

        event_summary = datastore.check_for_new_events(last_check_time)

        self.assertEqual(len(event_summary), 0)

    def test_jobs_check_for_updates(self):
        """ Cross-checks the number of Summaries given by the datastore function
            with the number of Summaries in the database after calling
            jobs.check_for_updates()
        """

        self.assertTrue(jobs.check_for_updates())

        last_check_time = time.mktime(datetime.date.fromtimestamp(0).timetuple())
        event_summary   = datastore.check_for_new_events(last_check_time)

        self.assertTrue(len(event_summary))

        # Cross-check event_summary with the database Summary

        count_need_updates = 0

        for date, station_list in event_summary.iteritems():
            for station, table_list in station_list.iteritems():
                if len(table_list) > 0:
                    count_need_updates += 1

        s = models.Summary.objects.filter(needs_update=True)

        self.assertEqual(count_need_updates, len(s))

    def test_jobs_check_for_updates_while_check_is_running(self):
        """ When an check_for_updates() is already running, a second call
            to check_for_updates() should return False.
        """

        state = models.GeneratorState.objects.get()
        state.check_is_running = True
        state.save()

        self.assertFalse(jobs.check_for_updates())

    def test_jobs_check_for_updates_at_the_end_of_epoch(self):
        """ Check for updates when the timestamp is 2**31 - 1. No summaries
            should be set to be updated. Unless we are past 2038..
        """

        state = models.GeneratorState.objects.get()
        state.check_last_run = datetime.datetime.fromtimestamp(2**31-1)
        state.save()

        self.assertTrue(jobs.check_for_updates())

        s = models.Summary.objects.filter(needs_update=True)

        self.assertEqual(len(s), 0)

    def test_jobs_update_all_histograms(self):
        """ Tests jobs.update_all_histograms() by processing a single Summary.
            It then checks for the output in the database
        """

        self.assertTrue(jobs.check_for_updates())

        #-----------------------------------------------------------------------
        # Make sure there is only 1 station that needs to be updated
        # 1. Pick one summary
        # 2. Set all summaries such that they don't need to be updated
        # 3. Set the chosen summary to be updated

        # 1. Pick one summary

        summaries = models.Summary.objects.filter(needs_update=True,
                                                  needs_update_events=True,
                                                  needs_update_config=True,
                                                  needs_update_weather=True)

        self.assertTrue(len(summaries) > 0)

        test_summary = summaries[0]

        # 2. Unset all summaries such that they don't need to be updated

        summaries = models.Summary.objects.filter(needs_update=True)

        for summary in summaries:
            summary.needs_update = False
            summary.needs_update_event = False
            summary.needs_update_config = False
            summary.needs_update_weather = False
            summary.save()

        test_summary.needs_update = True
        test_summary.needs_update_event = True
        test_summary.needs_update_config = True
        test_summary.needs_update_weather = True
        test_summary.save()

        # 3. Set the chosen summary to be updated

        summaries = models.Summary.objects.filter(needs_update=True)

        self.assertEqual(len(summaries), 1)

        summary = summaries[0]

        #-----------------------------------------------------------------------
        # Update everything for that one summary

        self.assertTrue(jobs.update_all_histograms())

        state = models.GeneratorState.objects.get()
        self.assertEqual(state.update_is_running, False)

        self.assertEqual(len(models.Summary.objects.filter(needs_update=True)), 0)

        # Check for pulseheight, pulseintegral and eventtime histograms

        histograms = models.DailyHistogram.objects.all()
        self.assertEqual(len(histograms), 3)

        for i in range(0, len(histograms) - 1):
            self.assertEqual(histograms[i].source, summary)

        # Check for config

        config = models.Configuration.objects.all()
        self.assertEqual(len(config), 1)
        self.assertEqual(config[0].source, summary)

        # Check for temperature and barometer datasets

        datasets = models.DailyDataset.objects.all()
        self.assertEqual(len(datasets), 2)

        for i in range(0, len(datasets) - 1):
            self.assertEqual(datasets[i].source, summary)

    def test_jobs_update_all_histograms_while_update_is_running(self):
        """ When an update_all_histograms() is already running, a second call
            to update_all_histograms() should return False.
        """

        state = models.GeneratorState.objects.get()
        state.update_is_running = True
        state.save()

        self.assertFalse(jobs.update_all_histograms())

