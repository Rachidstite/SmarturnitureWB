import unittest
from pathlib import Path


class TestDefaultPricingCatalog(unittest.TestCase):

    hardware_unit_prices = {
        "HINGE_BLUM_110_V1": 6.0,
        "MINIFIX_15_V1": 1.5,
        "DRAWER_SLIDE_STANDARD_450": 20.0,
        "TOUCH_LATCH_STANDARD": 45.0,
        "SCREW_4X40": 0.10,
        "SCREW_3_5X16": 0.08,
        "HANDLE_STANDARD_LOW": 6.0,
        "HANDLE_STANDARD_MID": 12.0,
        "HANDLE_STANDARD_HIGH": 20.0,
        "SLIDING_DOOR_HANDLE_METER": 30.0,
    }

    default_catalog_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "pricing"
        / "default_pricing_catalog.json"
    )

    def test_default_catalog_file_exists(self):

        self.assertTrue(
            self.default_catalog_path.exists(),
        )

    def test_default_catalog_loads_through_pricing_catalog_storage(self):

        from cost_intelligence.pricing_catalog import PricingCatalog
        from cost_intelligence.pricing_catalog_storage import (
            PricingCatalogStorage,
        )

        catalog = PricingCatalogStorage().load(
            self.default_catalog_path,
        )

        self.assertIsInstance(
            catalog,
            PricingCatalog,
        )

    def test_default_catalog_contains_mdf_18mm(self):

        from cost_intelligence.pricing_catalog_storage import (
            PricingCatalogStorage,
        )

        catalog = PricingCatalogStorage().load(
            self.default_catalog_path,
        )

        self.assertIsNotNone(
            catalog.get("MDF_18MM"),
        )

    def test_default_catalog_mdf_18mm_has_currency(self):

        from cost_intelligence.pricing_catalog_storage import (
            PricingCatalogStorage,
        )

        catalog = PricingCatalogStorage().load(
            self.default_catalog_path,
        )

        self.assertIn(
            "currency",
            catalog.get("MDF_18MM"),
        )

    def test_default_catalog_contains_each_hardware_sku(self):

        catalog = self._load_default_catalog()

        for sku in self.hardware_unit_prices:
            with self.subTest(sku=sku):
                self.assertIsNotNone(catalog.get(sku))

    def test_default_catalog_hardware_has_expected_unit_prices(self):

        catalog = self._load_default_catalog()

        for sku, expected_unit_price in self.hardware_unit_prices.items():
            with self.subTest(sku=sku):
                self.assertEqual(
                    catalog.get(sku)["unit_price"],
                    expected_unit_price,
                )

    def test_default_catalog_hardware_currency_is_mad(self):

        catalog = self._load_default_catalog()

        for sku in self.hardware_unit_prices:
            with self.subTest(sku=sku):
                self.assertEqual(
                    catalog.get(sku)["currency"],
                    "MAD",
                )

    def _load_default_catalog(self):

        from cost_intelligence.pricing_catalog_storage import (
            PricingCatalogStorage,
        )

        return PricingCatalogStorage().load(
            self.default_catalog_path,
        )


if __name__ == "__main__":
    unittest.main()
