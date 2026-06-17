import unittest
from pathlib import Path


class TestFactoryResourceCatalogService(unittest.TestCase):

    def test_service_exists(self):
        from manufacturing.factory_resource_catalog_service import (
            FactoryResourceCatalogService,
        )

        self.assertTrue(callable(FactoryResourceCatalogService().load))

    def test_missing_catalog_returns_empty_dict(self):
        from manufacturing.factory_resource_catalog_service import (
            FactoryResourceCatalogService,
        )

        service = FactoryResourceCatalogService(
            catalog_path=Path("/tmp/does-not-exist/factory_resource_catalog.json")
        )

        self.assertEqual(service.load(), {})

    def test_default_catalog_loads_factory_resource_values(self):
        from manufacturing.factory_resource_catalog_service import (
            FactoryResourceCatalogService,
        )

        catalog = FactoryResourceCatalogService().load()

        self.assertEqual(catalog["workers"], 3)
        self.assertEqual(catalog["cnc_machines"], 1)
        self.assertEqual(catalog["edge_banding_machines"], 1)
        self.assertEqual(catalog["assembly_stations"], 2)
        self.assertEqual(catalog["daily_work_hours"], 8)
        self.assertEqual(catalog["workdays_per_week"], 5)


if __name__ == "__main__":
    unittest.main()
