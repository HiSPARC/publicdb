import json
import urllib

from django.test import LiveServerTestCase

from publicdb.analysissessions.models import *


def is_json(response):

    for left, right in [(response.getcode(), 200),
                        (response.info().getmaintype(), "application"),
                        (response.info().getsubtype(), "json")]:
        if left != right:
            return False

    return True


class Client(object):

    """Client class for interacting with the server"""

    def __init__(self, testcase):
        self.testcase = testcase

    def receive_coincidence(self, session_title, session_pin, student_name):
        """Request data for a single coincidence"""

        params = urllib.urlencode({"session_title": session_title,
                                   "session_pin": session_pin,
                                   "student_name": student_name})
        response = urllib.urlopen('%s%s?%s' % (self.testcase.live_server_url,
                                               '/jsparc/get_coincidence/',
                                               params))
        return response

    def send_result(self, session_title, student_name, data):
        """Push data back to jSparc"""

        params = urllib.urlencode({"session_title": session_title,
                                   "student_name": student_name,
                                   "pk": data['pk'],
                                   "lat": data['events'][0]['lat'],
                                   "lon": data['events'][0]['lon'],
                                   "logEnergy": 15,
                                   "error": 1})
        response = urllib.urlopen('%s%s?%s' % (self.testcase.live_server_url,
                                               '/jsparc/result/',
                                               params))
        return response


class LiveSessionTestCase(LiveServerTestCase):

    fixtures = ['tests_inforecords',
                'tests_analysissessions',
                'tests_coincidences']

    def setUp(self):
        # Change start date and end date, otherwise it will complain the
        # session is not in progress anymore.

        session = AnalysisSession.objects.all()[0]

        session.starts = datetime.datetime.now() - datetime.timedelta(days=1)
        session.ends = datetime.datetime.now() + datetime.timedelta(days=365)
        session.save()

        super(LiveSessionTestCase, self).setUp()

    def test_everythingCorrect(self):
        client = Client(self)

        session = AnalysisSession.objects.all()[0]

        response = client.receive_coincidence(session.title, session.pin,
                                              "Student 1")
        assert(is_json(response))

        response = client.send_result(session.title, "Student 1",
                                      json.loads(response.read()))
        assert(is_json(response))

        data = json.loads(response.read())

        self.assertEqual(data['msg'], "OK [result stored]")

    def test_wrongPin(self):
        client = Client(self)

        session = AnalysisSession.objects.all()[0]

        try:
            client.receive_coincidence(session.title, 0000, "Student 1")
        except IOError, e:
            # raise IOError, ('http error', errcode, errmsg, headers)
            self.assertEqual(e[1], 401)
        else:
            self.assertTrue(False)

    def test_wrongTitle(self):
        client = Client(self)

        session = AnalysisSession.objects.all()[0]

        response = client.receive_coincidence(
            "Such a wrong title.. I guess!! l33t h4x0r!",
            session.pin,
            "Student 1")
        assert(not is_json(response))

    def test_wrongStudentName(self):
        client = Client(self)

        session = AnalysisSession.objects.all()[0]

        response = client.receive_coincidence(session.title, session.pin,
                                              "Student 1")
        assert(is_json(response))

        response = client.send_result(session.title, "Student 2",
                                      json.loads(response.read()))
        assert(not is_json(response))
