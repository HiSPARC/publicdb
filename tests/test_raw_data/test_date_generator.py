from datetime import date, datetime, timedelta

from django.test import SimpleTestCase

from publicdb.raw_data.date_generator import daterange, single_day_ranges


class TestDaterange(SimpleTestCase):
    def setUp(self):
        self.start = date(2010, 3, 1)

    def test_stop_is_start(self):
        self.assertEqual([self.start], list(daterange(self.start, self.start)))

    def test_stop_before_start(self):
        stop = self.start - timedelta(days=7)
        self.assertEqual([self.start], list(daterange(self.start, stop)))

    def test_stop_day_after_start(self):
        stop = self.start + timedelta(days=1)
        self.assertEqual([self.start, stop], list(daterange(self.start, stop)))

    def test_stop_days_after_start(self):
        stop = self.start + timedelta(days=3)
        self.assertEqual(
            [self.start, self.start + timedelta(days=1), self.start + timedelta(days=2), stop],
            list(daterange(self.start, stop)),
        )


class TestSingleDayRanges(SimpleTestCase):
    def setUp(self):
        self.start = datetime(2010, 3, 1, 5, 20, 13)

    def test_stop_is_start(self):
        self.assertEqual([(self.start, self.start)], list(single_day_ranges(self.start, self.start)))

    def test_stop_before_start(self):
        stop = self.start - timedelta(days=7)
        self.assertEqual([(self.start, stop)], list(single_day_ranges(self.start, stop)))

    def test_stop_end_of_same_day_as_start(self):
        stop = self.start.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.assertEqual([(self.start, stop)], list(single_day_ranges(self.start, stop)))

    def test_stop_days_after_start(self):
        stop = self.start + timedelta(days=3)
        midnight = self.start.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.assertEqual(
            [
                (self.start, midnight),
                (midnight, midnight + timedelta(days=1)),
                (midnight + timedelta(days=1), midnight + timedelta(days=2)),
                (midnight + timedelta(days=2), stop),
            ],
            list(single_day_ranges(self.start, stop)),
        )
