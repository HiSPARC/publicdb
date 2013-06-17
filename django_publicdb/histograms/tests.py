# Python
import datetime
import time
import string
import sys
import os
import code
import logging

import tables

# Django
from django.conf import settings
from django.test import TestCase, TransactionTestCase

# Publicdb
from django_publicdb.tests import datastore as tests_datastore
from django_publicdb.histograms import models, datastore, jobs

class BaseHistogramsTestCase(TransactionTestCase):

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

        try:
            data = tables.openFile(file, "r")
        except Exception:
            self.assertTrue(False)

        self.assertEqual(len(data.root.hisparc.cluster_amsterdam.station_501.events), 6843)
        data.close()

        # Download real data of station 505 on 20 January 2010, which has
        # data where we can fit the pulseheight MPV.

        date = datetime.date(2011, 7, 7)
        file = tests_datastore.get_datafile_path(date)

        if not os.path.exists(file):
            tests_datastore.download_data_station(501, date, get_blobs=True)

        self.assertTrue(os.path.exists(file))

        try:
            data = tables.openFile(file, "r")
        except Exception:
            self.assertTrue(False)

        self.assertEqual(len(data.root.hisparc.cluster_amsterdam.station_501.events), 63322)
        data.close()

        # Reset generator state such that it will always update when new files
        # are found

        state = models.GeneratorState.objects.get()
        state.update_last_run = datetime.datetime.fromtimestamp(0)
        state.check_last_run = datetime.datetime.fromtimestamp(0)
        state.save()

        super(BaseHistogramsTestCase, self).setUp()

    def tearDown(self):
        super(BaseHistogramsTestCase, self).tearDown()

        settings.DATASTORE_PATH = self.original_datastore_path

    #---------------------------------------------------------------------------
    # Tests
    #---------------------------------------------------------------------------

    #def test_interactive_shell(self, ):
    #    code.interact(local=dict(globals(), **locals()))


class DatastoreTestCase(BaseHistogramsTestCase):

    #---------------------------------------------------------------------------
    # Setup and teardown
    #---------------------------------------------------------------------------

    def setUp(self):
        super(DatastoreTestCase, self).setUp()

    def tearDown(self):
        super(DatastoreTestCase, self).tearDown()

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


class CheckForUpdatesTestCase(BaseHistogramsTestCase):

    #---------------------------------------------------------------------------
    # Setup and teardown
    #---------------------------------------------------------------------------

    def setUp(self):
        super(CheckForUpdatesTestCase, self).setUp()

    def tearDown(self):
        super(CheckForUpdatesTestCase, self).tearDown()

    #---------------------------------------------------------------------------
    # Tests
    #---------------------------------------------------------------------------

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

        #code.interact(local=dict(globals(), **locals()))

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


class PulseheightFitTestCase(BaseHistogramsTestCase):

    fixtures = [
        'tests_inforecords',
        'tests_histograms'
    ]

    #---------------------------------------------------------------------------
    # Setup and teardown
    #---------------------------------------------------------------------------

    def setUp(self):
        super(PulseheightFitTestCase, self).setUp()

        models.PulseheightFit.objects.all().delete()

        print "Checking for updates"
        self.assertTrue(jobs.check_for_updates())

        print "Updating ESD"
        jobs.update_esd()

    def tearDown(self):
        super(PulseheightFitTestCase, self).tearDown()

    #---------------------------------------------------------------------------
    # Tests
    #---------------------------------------------------------------------------

    def test_jobs_update_pulseheight_fit_normal(self, ):
        """ When everything is ok, in the end there should be 4 fits in the database
        """

        summary = models.Summary.objects.get(station__number=501,
                                             date = datetime.date(2011, 7, 7))

        jobs.update_pulseheight_fit(summary)

        # Four fits are expected

        fits = models.PulseheightFit.objects.all()

        self.assertEqual(len(fits), 4)

    def test_jobs_update_pulseheight_fit_no_config(self):
        """ When there is no config, no fit should have been made
        """

        models.Configuration.objects.all().delete()

        summary = models.Summary.objects.get(station__number=501,
                                             date = datetime.date(2011, 7, 7))

        jobs.update_pulseheight_fit(summary)

        # No fits are expected

        fits = models.PulseheightFit.objects.all()

        self.assertEqual(len(fits), 0)

    def test_jobs_save_pulseheight_fit_normal(self):
        """ Saving a PulseheightFit in normal conditions
        """

        summary = models.Summary.objects.get(station__number=501,
                                             date = datetime.date(2011, 7, 7))

        # Create and save fits into the database

        fits = []
        for numberOfPlate in range(1, 5):
            fits.append(
                models.PulseheightFit(
                    source = summary,
                    plate = int(numberOfPlate),

                    initial_mpv = 1,
                    initial_width = 2,

                    fitted_mpv = 3,
                    fitted_mpv_error = 4,
                    fitted_width = 5,
                    fitted_width_error = 6,

                    chi_square_reduced = 7))

        jobs.save_pulseheight_fits(summary, fits)

        # Updated value is expected

        fits = models.PulseheightFit.objects.filter(source = summary)
        self.assertEqual(len(fits), 4)
        self.assertEqual(fits[0].initial_mpv, 1.0)

    def test_jobs_save_pulseheight_fit_no_fits(self):
        """ Saving no fits should do nothing
        """

        summary = models.Summary.objects.get(station__number=501,
                                             date = datetime.date(2011, 7, 7))

        jobs.save_pulseheight_fits(summary, [])

        # No fits expected

        fits = models.PulseheightFit.objects.all()
        self.assertEqual(len(fits), 0)

    def test_jobs_save_pulseheight_fit_update(self):
        """ Updating a PulseheightFit should be reflected in the database
        """

        summary = models.Summary.objects.get(station__number=501,
                                             date = datetime.date(2011, 7, 7))

        numberOfPlate = 1

        # Create and save a fit into the database

        fit = models.PulseheightFit(
            source = summary,
            plate = int(numberOfPlate),

            initial_mpv = 1,
            initial_width = 2,

            fitted_mpv = 3,
            fitted_mpv_error = 4,
            fitted_width = 5,
            fitted_width_error = 6,

            chi_square_reduced = 7)

        fit.save()

        # Try to update an existing fit. What matters is that the source and
        # plate are the same, as the pair is defined to be unique in the table.

        fits = models.PulseheightFit.objects.filter(source = summary)
        self.assertEqual(len(fits), 1)

        fits[0].initial_mpv = 10

        jobs.save_pulseheight_fits(summary, fits)

        # Updated value is expected

        fits = models.PulseheightFit.objects.filter(source = summary)
        self.assertEqual(len(fits), 1)
        self.assertEqual(fits[0].initial_mpv, 10.0)


class UpdateAllHistogramsTestCase(BaseHistogramsTestCase):

    fixtures = [
        'tests_inforecords',
        'tests_histograms'
    ]

    #---------------------------------------------------------------------------
    # Setup and teardown
    #---------------------------------------------------------------------------

    def setUp(self):
        super(UpdateAllHistogramsTestCase, self).setUp()

        models.DailyHistogram.objects.all().delete()
        models.DailyDataset.objects.all().delete()
        models.PulseheightFit.objects.all().delete()

    def tearDown(self):
        super(UpdateAllHistogramsTestCase, self).tearDown()

    #---------------------------------------------------------------------------
    # Tests
    #---------------------------------------------------------------------------

    def test_jobs_update_all_histograms_while_update_is_running(self):
        """ When an update_all_histograms() is already running, a second call
            to update_all_histograms() should return False.
        """

        state = models.GeneratorState.objects.get()
        state.update_is_running = True
        state.save()

        self.assertFalse(jobs.update_all_histograms())

    def test_jobs_update_all_histograms_501_2011_7_7(self):
        """ Tests jobs.update_all_histograms() by processing a single Summary.
            It then checks for the output in the database. The data of station
            501 on 2011/7/7 contains events data that is suitable for fitting
            the pulseheight mpv.
        """

        # Prepare tables

        models.Summary.objects.filter(date__gte=datetime.date(2011, 7, 7)).delete()

        # Set the needs_update_x fields

        self.assertTrue(jobs.check_for_updates())

        #-----------------------------------------------------------------------
        # Make sure there is only 1 station that needs to be updated
        # 1. Pick one summary
        # 2. Unset all summaries such that they don't need to be updated

        # 1. Pick one summary
        # Should be for station 501 on 7 June 2011.

        summaries = models.Summary.objects.filter(date = datetime.date(2011, 7, 7))

        self.assertEqual(len(summaries), 1)

        test_summary = summaries[0]

        # 2. Unset all summaries such that they don't need to be updated

        summaries = models.Summary.objects.exclude(id=test_summary.id)

        for summary in summaries:
            summary.needs_update = False
            summary.needs_update_events = False
            summary.needs_update_config = False
            summary.needs_update_weather = False
            summary.save()

        #-----------------------------------------------------------------------
        # Update everything for that one summary

        self.assertTrue(jobs.update_all_histograms())

        state = models.GeneratorState.objects.get()
        self.assertEqual(state.update_is_running, False)

        self.assertEqual(len(models.Summary.objects.filter(needs_update=True)), 0)

        #-----------------------------------------------------------------------
        # Check for pulseheight, pulseintegral and eventtime histograms

        histograms = models.DailyHistogram.objects.filter(source__station__number=501,
                                                          source__date=datetime.date(2011, 7, 7))
        self.assertEqual(len(histograms), 3)

        for h in histograms:
            self.assertEqual(h.source, test_summary)

        #-----------------------------------------------------------------------
        # Check for pulseheight mpv fit

        fits = models.PulseheightFit.objects.all()
        self.assertEqual(len(fits), 4)

        self.assertTrue(222 < fits[0].fitted_mpv < 226)
        self.assertTrue(220 < fits[1].fitted_mpv < 224)
        self.assertTrue(240 < fits[2].fitted_mpv < 244)
        self.assertTrue(231 < fits[3].fitted_mpv < 235)

        #-----------------------------------------------------------------------
        # Check for temperature and barometer datasets

        datasets = models.DailyDataset.objects.filter(source__station__number=501,
                                                      source__date=datetime.date(2011, 7, 7))
        self.assertEqual(len(datasets), 2)

        for d in datasets:
            self.assertEqual(d.source, test_summary)

    def test_jobs_update_all_histograms_501_2012_5_16(self):
        """ Tests jobs.update_all_histograms() by processing a single Summary.
            It then checks for the output in the database. The data of station
            501 on 2012/5/16 contains events, configuration and weather data,
            but the events data is not enough to do a fit.
        """

        #-----------------------------------------------------------------------
        # Prepare tables

        models.Summary.objects.filter(date__gte=datetime.date(2012, 5, 16)).delete()

        # Set the needs_update_x fields

        self.assertTrue(jobs.check_for_updates())

        #-----------------------------------------------------------------------
        # Make sure there is only 1 station that needs to be updated
        # 1. Pick one summary
        # 2. Set all summaries such that they don't need to be updated
        # 3. Set the chosen summary to be updated

        # 1. Pick one summary
        # Should be for station 501 on 16 May 2012.

        summaries = models.Summary.objects.filter(date=datetime.date(2012, 5, 16))

        self.assertTrue(len(summaries) > 0)

        test_summary = summaries[0]

        # 2. Unset all summaries such that they don't need to be updated

        summaries = models.Summary.objects.exclude(id=test_summary.id)

        for summary in summaries:
            summary.needs_update = False
            summary.needs_update_events = False
            summary.needs_update_config = False
            summary.needs_update_weather = False
            summary.save()

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

        #-----------------------------------------------------------------------
        # Check for pulseheight, pulseintegral and eventtime histograms

        histograms = models.DailyHistogram.objects.filter(source__station__number=501,
                                                          source__date=datetime.date(2012, 5, 16))
        self.assertEqual(len(histograms), 3)

        for h in histograms:
            self.assertEqual(h.source, test_summary)

        #-----------------------------------------------------------------------
        # Check for config

        config = models.Configuration.objects.filter(source__station__number=501,
                                                     source__date=datetime.date(2012, 5, 16))
        self.assertEqual(len(config), 1)
        self.assertEqual(config[0].source, test_summary)

        #-----------------------------------------------------------------------
        # Check for temperature and barometer datasets

        datasets = models.DailyDataset.objects.filter(source__station__number=501,
                                                      source__date=datetime.date(2012, 5, 16))
        self.assertEqual(len(datasets), 2)

        for d in datasets:
            self.assertEqual(d.source, test_summary)
