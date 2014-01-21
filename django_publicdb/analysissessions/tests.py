import re
import datetime
import time
import string
import sys
import os
import json
import urllib

import tables

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

# Selenium WebDriver documentation:
# http://selenium.googlecode.com/svn/trunk/docs/api/py/webdriver_remote/selenium.webdriver.remote.webdriver.html

# Selenium WebElement (result of find_element method in webdriver) documentation:
# http://selenium.googlecode.com/svn/trunk/docs/api/py/webdriver_remote/selenium.webdriver.remote.webelement.html

from django.core import mail
from django.conf import settings
from django.test import LiveServerTestCase

from lib.test import datastore as test_datastore


class LiveSessionTestCase(LiveServerTestCase):
    fixtures = ['tests_inforecords']

    def setUp(self):
        # The tests require a data file. We will download some data and put it
        # in a test directory. It needs to be writable by the user who initiates
        # the tests.

        self.original_datastore_path = settings.DATASTORE_PATH
        path = os.path.join(settings.TEST_DATASTORE_PATH, "analysissessions")
        test_datastore.setup_test_datastore_directory(path)

        # Download real data of stations 3201, 3202 and 3203 on 25 March 2011.
        # There are 52 coincidences.

        date = datetime.date(2011, 3, 25)

        file = test_datastore.get_datafile_path(date)

        if not os.path.exists(file):
            test_datastore.download_data_station(3201, date, get_blobs=True)
            test_datastore.download_data_station(3202, date, get_blobs=True)
            test_datastore.download_data_station(3203, date, get_blobs=True)

        self.assertTrue(os.path.exists(file))

        try:
            data = tables.openFile(file, "r")
        except Exception:
            self.assertTrue(False)

        self.assertEqual(len(data.root.hisparc.cluster_leiden.station_3201.events), 50547)
        self.assertEqual(len(data.root.hisparc.cluster_leiden.station_3202.events), 43176)
        self.assertEqual(len(data.root.hisparc.cluster_leiden.station_3203.events), 18268)
        data.close()

        super(LiveSessionTestCase, self).setUp()

        # Start Selenium

        self.driver = webdriver.Firefox()

    def tearDown(self):
        super(LiveSessionTestCase, self).tearDown()

        settings.DATASTORE_PATH = self.original_datastore_path

        self.driver.quit()

    def changeUrlToLocal(self, url):
        return string.replace(url, 'http://data.hisparc.nl',
                              self.live_server_url)

    def test_RequestAnalysisSession(self):
        """
        Contents
        1. Request an analysis session via the website
        2. Check the email with the link to confirm a session request
        3. Initiate the creation of the session
        4. Check the email with the session details
        5. Simulate analyses sessions
        6. Check the results from the analyses sessions
        """

        driver = self.driver

        regexp_url = re.compile('http://\S+')

        number_of_students = 10

        # 1. Request an analysis session via the website

        #driver.get('%s%s' % (self.live_server_url, '/django/analysis-session/request/'))
        driver.get('%s%s' % (self.live_server_url, '/analysis-session/request/'))
        #driver.get('http://localhost:8081/django/analysis-session/request/')

        # Fill fields

        for field, input in [("id_first_name", "First"),
                             ("id_sur_name", "Sur"),
                             ("id_email", "test@test.test"),
                             ("id_school", "Test School"),
                             ("id_cluster", "Middelharnis"),
                             ("id_start_date_year", "2011"),
                             ("id_start_date_month", "March"),
                             ("id_start_date_day", "25"),
                             ("id_number_of_events", "10")]:
            inputElement = driver.find_element_by_id(field)
            inputElement.send_keys(input)

        # CLICK

        inputElement.submit()

        # 2. Check the email with the link to confirm a session request
        time.sleep(1)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["test@test.test"])

        # Extract the link in the mail

        match = regexp_url.search(mail.outbox[0].body)

        self.assertNotEqual(match, None)

        url_requesting_session = self.changeUrlToLocal(match.group(0))

        driver.get(url_requesting_session)


        # 3. Initiate the creation of the session

        driver.get('%s%s' %
                   (self.live_server_url, '/analysis-session/request/create'))

        # 4. Check the email with the session details

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].to, ["test@test.test"])

        print mail.outbox[1].body
        sys.stdout.flush()

        for var_name, regexp in [
                ("session_title", r"^.*Title = (.+)$"),
                ("session_pin", r"^.*Pin = (\S+)$"),
                ("session_events", r"^.*Events created = (\S+)$"),
                ("url_session_results", r".*(http://\S+/analysis-session/\S+)$")]:
            match = re.search(regexp, mail.outbox[1].body, re.MULTILINE)

            self.assertNotEqual(match, None)

            exec(var_name + " = '" + self.changeUrlToLocal(match.group(1)) + "'")

        self.assertEqual(session_events, '52')


        # 5. Simulate analyses sessions

        # Let's simulate some students

        for student_nr in range(1, number_of_students):

            print "Simulating student nr %s..." % student_nr

            # Request data for a single coincidence

            params = urllib.urlencode({
                "session_title": session_title,
                "session_pin": session_pin,
                "student_name": "Student %s" % student_nr})

            response = urllib.urlopen(
                '%s%s?%s' %
                (self.live_server_url, '/jsparc/get_coincidence/', params))

            self.assertEqual(response.getcode(), 200)
            self.assertEqual(response.info().getmaintype(), "application")
            self.assertEqual(response.info().getsubtype(),  "json")

            data = json.loads(response.read())

            # Push data back to jSparc

            params = urllib.urlencode({
                "session_title": session_title,
                "student_name": "Student %s" % student_nr,
                "pk": data['pk'],
                "lat": data['events'][0]['lat'],
                "lon": data['events'][0]['lon'],
                "logEnergy": 15,
                "error": 1})

            response = urllib.urlopen(
                '%s%s?%s' % (self.live_server_url, '/jsparc/result/', params))

            self.assertEqual(response.getcode(), 200)
            self.assertEqual(response.info().getmaintype(), "application")
            self.assertEqual(response.info().getsubtype(), "json")

            data = json.loads(response.read())

            self.assertEqual(data['msg'], "OK [result stored]")


        # 6. Check the results from the analyses sessions

        driver.get(url_session_results)

        table = driver.find_element_by_tag_name("table")

        # Check the number of students

        self.assertEqual(number_of_students,
                         len(table.find_elements_by_tag_name("tr")))

        # Check whether the energy spectrum exists on the server

        #image = driver.find_element_xpath("div[@id=energyHistogram]/img")
        #image_url = image.get_attribute("src")

        #driver.get(image_url)

