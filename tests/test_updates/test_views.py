from datetime import date, timedelta
from tempfile import mkdtemp
from urlparse import parse_qs

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..factories.updates_factories import AdminUpdateFactory, UserUpdateFactory, InstallerUpdateFactory


@override_settings(MEDIA_ROOT=mkdtemp(prefix='mediaroot'))
class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_update = AdminUpdateFactory(queue__slug='hisparc')
        self.user_update = UserUpdateFactory(queue__slug='hisparc')
        self.installer_update = InstallerUpdateFactory(queue__slug='hisparc')

    def test_latest_installer(self):
        response = self.client.get(reverse('updates:latest'))
        self.assertEqual(302, response.status_code)
        self.assertEqual(self.installer_update.installer.url, response['Location'])

    def test_check_querystring_no_update(self):
        kwargs = {'queue': 'hisparc'}
        query = {'admin_version': 1, 'user_version': 1}
        response = self.client.get(reverse('updates:check', kwargs=kwargs), query)
        self.assertEqual(200, response.status_code)

        data = parse_qs(response.content)
        self.assertEqual({'mustUpdate': ['0']}, data)

    def test_check_querystring_admin_update(self):
        kwargs = {'queue': 'hisparc'}
        query = {'admin_version': 1, 'user_version': 1}
        admin_update = AdminUpdateFactory(update__filename='admin_update_v2.exe', queue__slug='hisparc')

        response = self.client.get(reverse('updates:check', kwargs=kwargs), query)
        self.assertEqual(200, response.status_code)

        data = parse_qs(response.content)
        self.assertEqual(
            {'mustUpdate': ['2'], 'newVersionAdmin': ['2'], 'urlAdmin': [admin_update.update.url]},
            data)

    def test_check_querystring_user_update(self):
        kwargs = {'queue': 'hisparc'}
        query = {'admin_version': 1, 'user_version': 1}
        user_update = UserUpdateFactory(update__filename='user_update_v2.exe', queue__slug='hisparc')

        response = self.client.get(reverse('updates:check', kwargs=kwargs), query)
        self.assertEqual(200, response.status_code)

        data = parse_qs(response.content)
        self.assertEqual(
            {'mustUpdate': ['1'], 'newVersionUser': ['2'], 'urlUser': [user_update.update.url]},
            data)

    def test_check_querystring_admin_and_user_update(self):
        kwargs = {'queue': 'hisparc'}
        query = {'admin_version': 1, 'user_version': 1}
        admin_update = AdminUpdateFactory(update__filename='admin_update_v2.exe', queue__slug='hisparc')
        user_update = UserUpdateFactory(update__filename='user_update_v2.exe', queue__slug='hisparc')

        response = self.client.get(reverse('updates:check', kwargs=kwargs), query)
        self.assertEqual(200, response.status_code)

        data = parse_qs(response.content)
        self.assertEqual(
            {'mustUpdate': ['3'],
             'newVersionUser': ['2'], 'urlUser': [user_update.update.url],
             'newVersionAdmin': ['2'], 'urlAdmin': [admin_update.update.url]},
            data)
