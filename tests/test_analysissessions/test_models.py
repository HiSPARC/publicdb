import datetime
import hashlib

from django.test import TestCase

from ..factories.analysissessions_factories import (AnalysisSessionFactory, AnalyzedCoincidenceFactory,
                                                    SessionRequestFactory, StudentFactory)
from ..factories.inforecords_factories import ClusterFactory


class TestAnalysisSession(TestCase):
    def setUp(self):
        super(TestAnalysisSession, self).setUp()
        self.cluster = ClusterFactory(number=0, country__number=0)
        self.analysis_session = AnalysisSessionFactory(session_request__cluster=self.cluster)

    def test_in_progress(self):
        self.assertTrue(self.analysis_session.in_progress())

    def test_no_longer_in_progress(self):
        analysis_session = AnalysisSessionFactory(
            session_request__cluster=self.cluster,
            starts=datetime.datetime.utcnow() + datetime.timedelta(days=3),
            ends=datetime.datetime.utcnow() + datetime.timedelta(days=7))
        self.assertFalse(analysis_session.in_progress())

    def test_not_yet_in_progress(self):
        analysis_session = AnalysisSessionFactory(
            session_request__cluster=self.cluster,
            starts=datetime.datetime.utcnow() - datetime.timedelta(days=7),
            ends=datetime.datetime.utcnow() - datetime.timedelta(days=3))
        self.assertFalse(analysis_session.in_progress())

    def test_hash(self):
        self.assertEqual(hashlib.md5(self.analysis_session.slug).hexdigest(), self.analysis_session.hash)

    def test_str(self):
        self.assertEqual(self.analysis_session.title, str(self.analysis_session))

    def test_test_student(self):
        # Each session should get a Test student when created.
        self.analysis_session.students.get(name='Test student')


class TestStudent(TestCase):
    def setUp(self):
        super(TestStudent, self).setUp()
        cluster = ClusterFactory(number=0, country__number=0)
        self.student = StudentFactory(name='Eugene', session__title='VU1', session__session_request__cluster=cluster)

    def test_str(self):
        self.assertEqual('VU1 - Eugene', str(self.student))


class TestAnalyzedCoincidence(TestCase):
    def setUp(self):
        super(TestAnalyzedCoincidence, self).setUp()
        cluster = ClusterFactory(number=0, country__number=0)
        session_request = SessionRequestFactory(cluster=cluster)
        session = AnalysisSessionFactory(session_request=session_request)
        self.analyzed_coincidence = AnalyzedCoincidenceFactory(session=session, student__session=session)

    def test_str(self):
        self.assertEqual(
            '%s - %s' % (self.analyzed_coincidence.coincidence, self.analyzed_coincidence.student),
            str(self.analyzed_coincidence))


class TestSessionRequest(TestCase):
    def setUp(self):
        super(TestSessionRequest, self).setUp()
        self.cluster = ClusterFactory(number=0, country__number=0)

    def test_session_request(self):
        self.session_request = SessionRequestFactory(cluster=self.cluster)
