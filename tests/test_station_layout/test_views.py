from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from ..factories.inforecords_factories import StationFactory
from ..factories.station_layout_factories import StationLayoutQuarantineFactory


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.station = StationFactory(number=1, cluster__number=0, cluster__country__number=0)
        super(TestViews, self).setUp()

    def get_html(self, url):
        """Get url and check if the response is OK and valid json"""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])
        return response

    def test_submit(self):
        self.get_html(reverse('layout:submit'))

    def test_confirm(self):
        layout = StationLayoutQuarantineFactory(station=self.station, email_verified=False)
        kwargs = {'hash': layout.hash_submit}
        self.get_html(reverse('layout:confirm', kwargs=kwargs))

        layout.refresh_from_db()
        self.assertTrue(layout.email_verified)
        self.assertEqual(1, len(mail.outbox))

    def test_review(self):
        layout = StationLayoutQuarantineFactory(station=self.station, email_verified=True, reviewed=False)
        kwargs = {'hash': layout.hash_review}
        self.get_html(reverse('layout:review', kwargs=kwargs))
