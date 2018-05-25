from django.test import TestCase

from ..factories.inforecords_factories import StationFactory
from ..factories.station_layout_factories import StationLayoutFactory


class TestModels(TestCase):
    def setUp(self):
        self.station = StationFactory(number=1, cluster__number=0, cluster__country__number=0)
        super(TestModels, self).setUp()

    def test_has_four_detectors(self):
        """Check property to verify number of detectors"""
        layout = StationLayoutFactory(station=self.station)
        self.assertTrue(layout.has_four_detectors)

    def test_does_not_have_four_detectors(self):
        """Check property to verify not four detectors"""
        layout = StationLayoutFactory(
            station=self.station,
            detector_3_radius=None,
            detector_3_alpha=None,
            detector_3_height=None,
            detector_3_beta=None,
            detector_4_radius=None,
            detector_4_alpha=None,
            detector_4_height=None,
            detector_4_beta=None
        )
        self.assertFalse(layout.has_four_detectors)
