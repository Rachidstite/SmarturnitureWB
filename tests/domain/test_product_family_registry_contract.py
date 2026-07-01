import inspect
import unittest
from dataclasses import fields, is_dataclass

import domain.product_family_registry as registry_module
from domain.product_family import ProductFamily
from domain.product_family_registry import ProductFamilyRegistry


class TestProductFamilyRegistryContract(unittest.TestCase):
    def test_registry_is_dataclass(self):
        self.assertTrue(is_dataclass(ProductFamilyRegistry))
        self.assertEqual(
            [field.name for field in fields(ProductFamilyRegistry)],
            ["product_families"],
        )

    def test_safe_defaults(self):
        registry = ProductFamilyRegistry()

        self.assertEqual(registry.product_families, {})
        self.assertIsNone(registry.get("UNKNOWN"))
        self.assertFalse(registry.contains("UNKNOWN"))

    def test_default_dicts_are_independent(self):
        first = ProductFamilyRegistry()
        second = ProductFamilyRegistry()

        first.product_families["BASE_CABINET"] = ProductFamily(family_id="BASE_CABINET")

        self.assertEqual(second.product_families, {})
        self.assertIsNot(first.product_families, second.product_families)

    def test_can_register_base_cabinet_product_family(self):
        family = ProductFamily(
            family_id="BASE_CABINET",
            name="Base Cabinet",
            category="kitchen",
        )

        original = ProductFamilyRegistry()
        updated = original.with_family(family)

        self.assertEqual(original.product_families, {})
        self.assertTrue(updated.contains("BASE_CABINET"))
        self.assertIs(updated.get("BASE_CABINET"), family)

    def test_can_retrieve_by_family_id(self):
        family = ProductFamily(family_id="WARDROBE", name="Wardrobe")
        registry = ProductFamilyRegistry().with_family(family)

        self.assertIs(registry.get("WARDROBE"), family)

    def test_missing_family_returns_none(self):
        registry = ProductFamilyRegistry()

        self.assertIsNone(registry.get("WALL_CABINET"))

    def test_no_engine_builder_renderer_manufacturing_cost_or_commercial_dependencies(self):
        source = inspect.getsource(registry_module)
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
            "manufacturing",
            "cost",
            "commercial",
        )
        for line in import_lines:
            for token in forbidden:
                self.assertNotIn(token, line)


if __name__ == "__main__":
    unittest.main()
