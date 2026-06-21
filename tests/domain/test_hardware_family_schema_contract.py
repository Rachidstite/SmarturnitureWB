import json
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path


class TestHardwareFamilySchemaContract(unittest.TestCase):

    def test_hardware_spec_exposes_hardware_family(self):
        from domain.hardware_library import HardwareSpec

        field_names = [field.name for field in fields(HardwareSpec)]

        self.assertIn("hardware_family", field_names)

    def test_builtin_hardware_definitions_expose_correct_hardware_family(self):
        from domain.hardware_library import HardwareRegistry

        registry = HardwareRegistry()

        expectations = {
            "MINIFIX_15_V1": "MINIFIX",
            "CONFIRMAT_50_V1": "CONFIRMAT",
            "SHELF_PIN_5MM": "SHELF_PIN",
            "DRAWER_SLIDE_SOFTCLOSE_450": "DRAWER_SLIDE",
            "DRAWER_SLIDE_STANDARD_450": "DRAWER_SLIDE",
        }

        for sku, hardware_family in expectations.items():
            with self.subTest(sku=sku):
                hardware = registry.get_hardware(sku)
                self.assertIsNotNone(hardware)
                self.assertEqual(hardware.hardware_family, hardware_family)

    def test_hardware_catalog_loader_preserves_hardware_family_from_json(self):
        from domain.hardware_catalog_loader import HardwareCatalogLoader

        payload = {
            "items": [
                {
                    "sku": "CUSTOM_CONNECTOR_X1",
                    "hardware_family": "CUSTOM_CONNECTOR",
                    "manufacturer": "GENERIC",
                    "model": "X1",
                    "revision": "1.0",
                    "category": "CONNECTORS",
                    "price": 1.0,
                    "host_holes": [
                        {
                            "diameter": 5.0,
                            "depth": 12.0,
                            "face": "LEFT",
                            "axis": "Z",
                            "offset_x": 0.0,
                            "offset_y": 0.0,
                            "is_through_hole": False,
                        }
                    ],
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "hardware.json"
            catalog_path.write_text(json.dumps(payload), encoding="utf-8")

            catalog = HardwareCatalogLoader.load(catalog_path)

        self.assertIn("CUSTOM_CONNECTOR_X1", catalog)
        self.assertEqual(
            catalog["CUSTOM_CONNECTOR_X1"].hardware_family,
            "CUSTOM_CONNECTOR",
        )

    def test_legacy_catalog_rows_remain_loadable_with_safe_default_family(self):
        from domain.hardware_catalog_loader import HardwareCatalogLoader

        payload = {
            "items": [
                {
                    "sku": "LEGACY_CUSTOM_X2",
                    "manufacturer": "GENERIC",
                    "model": "X2",
                    "revision": "1.0",
                    "category": "CONNECTORS",
                    "price": 1.0,
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "legacy_hardware.json"
            catalog_path.write_text(json.dumps(payload), encoding="utf-8")

            catalog = HardwareCatalogLoader.load(catalog_path)

        self.assertIn("LEGACY_CUSTOM_X2", catalog)
        self.assertEqual(getattr(catalog["LEGACY_CUSTOM_X2"], "hardware_family", ""), "")


if __name__ == "__main__":
    unittest.main()
