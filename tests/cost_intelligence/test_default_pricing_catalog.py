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

    edge_banding_prices_per_meter = {
        "ABS_1MM": 5.0,
        "PVC_0.4MM": 1.5,
        "PVC_1MM": 5.0,
        "PVC_2MM": 5.0,
    }

    machining_prices_per_operation = {
        "MACHINING_DRILL": 1.5,
        "MACHINING_ROUTE": 8.0,
        "MACHINING_GROOVE": 5.0,
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

    def test_default_catalog_contains_each_edge_banding_sku(self):

        catalog = self._load_default_catalog()

        for sku in self.edge_banding_prices_per_meter:
            with self.subTest(sku=sku):
                self.assertIsNotNone(catalog.get(sku))

    def test_default_catalog_edge_banding_has_expected_price_per_meter(self):

        catalog = self._load_default_catalog()

        for sku, expected_price in self.edge_banding_prices_per_meter.items():
            with self.subTest(sku=sku):
                self.assertEqual(
                    catalog.get(sku)["price_per_meter"],
                    expected_price,
                )

    def test_default_catalog_edge_banding_currency_is_mad(self):

        catalog = self._load_default_catalog()

        for sku in self.edge_banding_prices_per_meter:
            with self.subTest(sku=sku):
                self.assertEqual(
                    catalog.get(sku)["currency"],
                    "MAD",
                )

    def test_default_catalog_contains_each_machining_operation_key(self):

        catalog = self._load_default_catalog()

        for key in self.machining_prices_per_operation:
            with self.subTest(key=key):
                self.assertIsNotNone(catalog.get(key))

    def test_default_catalog_machining_has_expected_price_per_operation(self):

        catalog = self._load_default_catalog()

        for key, expected_price in self.machining_prices_per_operation.items():
            with self.subTest(key=key):
                self.assertEqual(
                    catalog.get(key)["price_per_operation"],
                    expected_price,
                )

    def test_default_catalog_machining_currency_is_mad(self):

        catalog = self._load_default_catalog()

        for key in self.machining_prices_per_operation:
            with self.subTest(key=key):
                self.assertEqual(
                    catalog.get(key)["currency"],
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
