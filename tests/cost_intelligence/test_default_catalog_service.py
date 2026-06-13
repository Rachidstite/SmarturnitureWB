import unittest


class TestDefaultCatalogService(unittest.TestCase):

    def test_service_loads_default_catalog(self):

        from cost_intelligence.default_catalog_service import (
            DefaultCatalogService,
        )

        catalog = DefaultCatalogService().load_default_catalog()

        self.assertTrue(
            catalog.prices,
        )

    def test_service_returns_pricing_catalog(self):

        from cost_intelligence.default_catalog_service import (
            DefaultCatalogService,
        )
        from cost_intelligence.pricing_catalog import PricingCatalog

        catalog = DefaultCatalogService().load_default_catalog()

        self.assertIsInstance(
            catalog,
            PricingCatalog,
        )

    def test_default_catalog_contains_mdf_18mm(self):

        from cost_intelligence.default_catalog_service import (
            DefaultCatalogService,
        )

        catalog = DefaultCatalogService().load_default_catalog()

        self.assertIsNotNone(
            catalog.get("MDF_18MM"),
        )


if __name__ == "__main__":
    unittest.main()
