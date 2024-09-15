from django.test import TestCase

from publicdb.status_display.templatetags import fix_strings


class TestFixStrings(TestCase):
    def test_remove_hyphens(self):
        self.assertEqual('', fix_strings.remove_hyphens(''))
        self.assertEqual('', fix_strings.remove_hyphens('-'))
        self.assertEqual('', fix_strings.remove_hyphens('--'))
        self.assertEqual('WithoutHyphens', fix_strings.remove_hyphens('-Without-Hyphens'))

