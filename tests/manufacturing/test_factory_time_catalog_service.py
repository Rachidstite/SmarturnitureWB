import unittest
from pathlib import Path


class TestFactoryTimeCatalogService(unittest.TestCase):

    def test_service_exists(self):
        from manufacturing.factory_time_catalog_service import (
            FactoryTimeCatalogService,
        )

        self.assertTrue(callable(FactoryTimeCatalogService().load))

    def test_missing_catalog_returns_empty_dict(self):
        from manufacturing.factory_time_catalog_service import (
            FactoryTimeCatalogService,
        )

        service = FactoryTimeCatalogService(
            catalog_path=Path("/tmp/does-not-exist/factory_time_catalog.json")
        )

        self.assertEqual(service.load(), {})

    def test_default_catalog_loads_factory_time_values(self):
        from manufacturing.factory_time_catalog_service import (
            FactoryTimeCatalogService,
        )

        catalog = FactoryTimeCatalogService().load()

        self.assertEqual(catalog["drill_minutes_per_operation"], 0.5)
        self.assertEqual(catalog["edge_banding_minutes_per_meter"], 0.5)
        self.assertEqual(catalog["assembly_minutes_per_panel"], 6.0)
        self.assertEqual(catalog["cnc_minutes_per_panel"], 1.0)


if __name__ == "__main__":
    unittest.main()
