import inspect
import unittest
from dataclasses import asdict

import domain.product_family_catalog as catalog_module
from domain.product_family import ProductFamily
from domain.product_family_registry import ProductFamilyRegistry


class TestProductFamilyCatalogContract(unittest.TestCase):
    def test_built_in_families_are_product_family_instances(self):
        self.assertIsInstance(catalog_module.BASE_CABINET, ProductFamily)
        self.assertIsInstance(catalog_module.WALL_CABINET, ProductFamily)
        self.assertIsInstance(catalog_module.TALL_CABINET, ProductFamily)

    def test_registry_contains_all_three_families(self):
        registry = catalog_module.BUILT_IN_PRODUCT_FAMILY_REGISTRY

        self.assertIsInstance(registry, ProductFamilyRegistry)
        self.assertTrue(registry.contains("BASE_CABINET"))
        self.assertTrue(registry.contains("WALL_CABINET"))
        self.assertTrue(registry.contains("TALL_CABINET"))

    def test_families_have_stable_ids(self):
        self.assertEqual(catalog_module.BASE_CABINET.family_id, "BASE_CABINET")
        self.assertEqual(catalog_module.WALL_CABINET.family_id, "WALL_CABINET")
        self.assertEqual(catalog_module.TALL_CABINET.family_id, "TALL_CABINET")

    def test_defaults_are_data_only(self):
        base_data = asdict(catalog_module.BASE_CABINET)
        wall_data = asdict(catalog_module.WALL_CABINET)
        tall_data = asdict(catalog_module.TALL_CABINET)

        self.assertEqual(base_data["default_parameters"]["width_mm"], 600.0)
        self.assertEqual(wall_data["default_parameters"]["depth_mm"], 350.0)
        self.assertEqual(tall_data["default_parameters"]["height_mm"], 2100.0)
        self.assertTrue(base_data["manufacturing_defaults"]["edge_banding_required"])
        self.assertTrue(wall_data["engineering_defaults"]["has_back_panel"])
        self.assertEqual(tall_data["commercial_defaults"]["pricing_group"], "STANDARD_TALL")

    def test_no_engine_builder_renderer_manufacturing_cost_or_commercial_imports(self):
        source = inspect.getsource(catalog_module)
        import_lines = [
            line.strip()
            for line in source.splitlines()
            if line.strip().startswith("import ") or line.strip().startswith("from ")
        ]

        forbidden = (
            "Builder",
            "Engine",
            "Renderer",
            "FreeCAD",
            "SceneGraph",
            "Geometry",
            "manufacturing",
            "cost",
            "commercial",
        )
        for line in import_lines:
            for token in forbidden:
                self.assertNotIn(token, line)


if __name__ == "__main__":
    unittest.main()
