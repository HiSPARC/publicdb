from django.test import TestCase

from publicdb.status_display.templatetags import fix_data


class TestFixData(TestCase):
    def test_fix_histogram_data(self):
        self.assertEqual([[1, 2.1], [2, 2.2], [3, 2.2]], fix_data.fix_histogram_data([[1, 2.1], [2, 2.2]]))
        self.assertEqual([[1, 2.1], [10, 2.2], [19, 2.2]], fix_data.fix_histogram_data([[1, 2.1], [10, 2.2]]))

    def test_fix_timestamps(self):
        self.assertEqual([[1_000, 2.1], [2_000, 2.2]], fix_data.fix_timestamps([[1, 2.1], [2, 2.2]]))

    def test_fix_timestamps_in_data(self):
        dataset = [
            [1647993600, 98],
            [1647993780, 99],
            [1648079820, 1],
        ]
        self.assertEqual(
            [[0, 98], [0.05, 99], [23.95, 1]],
            fix_data.fix_timestamps_in_data(dataset),
        )

    def test_slice_data(self):
        result = fix_data.slice_data([1] * 2_000, 200)
        self.assertEqual(10, len(result))
        self.assertEqual([1] * 10, result)

    def test_round_data(self):
        self.assertEqual([[1, 2]], fix_data.round_data([[1, 2.11]], 0))
        self.assertEqual([[1, 2.1]], fix_data.round_data([[1, 2.11]], 1))
        self.assertEqual([[2.0, 2.2]], fix_data.round_data([[1.99, 2.16]], 1))

    def test_shift_bins(self):
        self.assertEqual([[2, 2.1], [3, 2.2]], fix_data.shift_bins([[1, 2.1], [2, 2.2]], 1))

    def test_none_to_nan(self):
        self.assertEqual('nan', fix_data.none_to_nan(None))

        for value in [0., 0, 1, '', 'this']:
            self.assertEqual(value, fix_data.none_to_nan(value))

    def test_mv_to_adc(self):
        self.assertEqual(30, fix_data.mv_to_adc(30))
        self.assertEqual(30, fix_data.mv_to_adc(30.))
        self.assertEqual(30.7, fix_data.mv_to_adc(30.7))
        self.assertEqual(323, fix_data.mv_to_adc(-70))
        self.assertEqual(253, fix_data.mv_to_adc(-30))
