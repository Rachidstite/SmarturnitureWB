import unittest

from domain.anchors import MountFace
from domain.hardware_library import HardwareRegistry


class TestHardwareRegistry(unittest.TestCase):

    NEW_HARDWARE = {
        "DRAWER_SLIDE_STANDARD_450": (20.0, "DRAWER_SLIDES"),
        "TOUCH_LATCH_STANDARD": (45.0, "LATCHES"),
        "SCREW_4X40": (0.10, "SCREWS"),
        "SCREW_3_5X16": (0.08, "SCREWS"),
        "HANDLE_STANDARD_LOW": (6.0, "HANDLES"),
        "HANDLE_STANDARD_MID": (12.0, "HANDLES"),
        "HANDLE_STANDARD_HIGH": (20.0, "HANDLES"),
        "SLIDING_DOOR_HANDLE_METER": (30.0, "HANDLES"),
    }

    def setUp(self):
        self.registry = HardwareRegistry()

    def test_existing_hardware_still_exists(self):
        self.assertIsNotNone(self.registry.get_hardware("MINIFIX_15_V1"))
        self.assertIsNotNone(self.registry.get_hardware("HINGE_BLUM_110_V1"))

    def test_new_hardware_skus_exist(self):
        for sku in self.NEW_HARDWARE:
            with self.subTest(sku=sku):
                self.assertIsNotNone(self.registry.get_hardware(sku))

    def test_new_hardware_has_expected_price(self):
        for sku, (expected_price, _expected_category) in self.NEW_HARDWARE.items():
            with self.subTest(sku=sku):
                hardware = self.registry.get_hardware(sku)

                self.assertEqual(hardware.price, expected_price)

    def test_new_hardware_has_expected_category(self):
        for sku, (_expected_price, expected_category) in self.NEW_HARDWARE.items():
            with self.subTest(sku=sku):
                hardware = self.registry.get_hardware(sku)

                self.assertEqual(hardware.category, expected_category)

    def test_display_name_still_returns_manufacturer_and_model(self):
        hardware = self.registry.get_hardware("DRAWER_SLIDE_STANDARD_450")

        self.assertEqual(hardware.display_name, "GENERIC STANDARD_SLIDE_450")

    def test_drawer_slide_softclose_has_basic_host_holes(self):
        hardware = self.registry.get_hardware("DRAWER_SLIDE_SOFTCLOSE_450")

        self.assertEqual(len(hardware.host_holes), 2)
        self._assert_drawer_slide_holes(hardware.host_holes)

    def test_drawer_slide_standard_has_basic_host_holes(self):
        hardware = self.registry.get_hardware("DRAWER_SLIDE_STANDARD_450")

        self.assertEqual(len(hardware.host_holes), 2)
        self._assert_drawer_slide_holes(hardware.host_holes)

    def _assert_drawer_slide_holes(self, holes):
        self.assertEqual(
            {hole.offset_y for hole in holes},
            {50.0, 350.0},
        )
        for hole in holes:
            self.assertEqual(hole.diameter, 3.0)
            self.assertEqual(hole.depth, 12.0)
            self.assertEqual(hole.face, MountFace.LEFT)
            self.assertEqual(hole.offset_x, 32.0)


if __name__ == "__main__":
    unittest.main()
