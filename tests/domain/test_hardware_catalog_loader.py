import unittest
from pathlib import Path

from domain.anchors import MountFace


class TestHardwareCatalogLoader(unittest.TestCase):

    def test_loader_returns_empty_dict_for_missing_file(self):
        from domain.hardware_catalog_loader import HardwareCatalogLoader

        self.assertEqual(
            HardwareCatalogLoader.load(
                Path("/tmp/does-not-exist/hardware_catalog.json")
            ),
            {},
        )

    def test_loader_loads_drawer_slide_json(self):
        from domain.hardware_catalog_loader import HardwareCatalogLoader

        catalog = HardwareCatalogLoader.load(
            Path(__file__).resolve().parents[2]
            / "data"
            / "hardware"
            / "drawer_slides.json"
        )

        self.assertIn("DRAWER_SLIDE_STANDARD_450", catalog)
        spec = catalog["DRAWER_SLIDE_STANDARD_450"]
        self.assertEqual(spec.price, 20.0)
        self.assertEqual(spec.category, "DRAWER_SLIDES")
        self.assertEqual(spec.display_name, "GENERIC STANDARD_SLIDE_450")
        self.assertEqual(len(spec.host_holes), 2)
        self.assertEqual(
            {hole.offset_y for hole in spec.host_holes},
            {50.0, 350.0},
        )
        for hole in spec.host_holes:
            self.assertEqual(hole.diameter, 3.0)
            self.assertEqual(hole.depth, 12.0)
            self.assertEqual(hole.face, MountFace.LEFT)
            self.assertEqual(hole.axis, "Z")
            self.assertEqual(hole.offset_x, 32.0)
            self.assertFalse(hole.is_through_hole)

    def test_registry_still_resolves_loaded_drawer_slide_sku(self):
        from domain.hardware_library import HardwareRegistry

        registry = HardwareRegistry()
        hardware = registry.get_hardware("DRAWER_SLIDE_STANDARD_450")

        self.assertIsNotNone(hardware)
        self.assertEqual(len(hardware.host_holes), 2)
        self.assertEqual(
            {hole.offset_y for hole in hardware.host_holes},
            {50.0, 350.0},
        )


if __name__ == "__main__":
    unittest.main()
