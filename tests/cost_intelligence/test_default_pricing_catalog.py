import unittest
from pathlib import Path


class TestDefaultPricingCatalog(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()
