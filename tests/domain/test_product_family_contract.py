import inspect
import unittest
from dataclasses import asdict, fields, is_dataclass

import domain.product_family as product_family_module
from domain.product_family import ProductFamily


class TestProductFamilyContract(unittest.TestCase):
    def test_product_family_is_a_dataclass(self):
        self.assertTrue(is_dataclass(ProductFamily))

    def test_field_inventory_is_stable(self):
        self.assertEqual(
            [field.name for field in fields(ProductFamily)],
            [
                "family_id",
                "name",
                "category",
                "description",
                "default_parameters",
                "engineering_defaults",
                "manufacturing_defaults",
                "visual_defaults",
                "commercial_defaults",
                "metadata",
            ],
        )

    def test_safe_defaults(self):
        family = ProductFamily()

        self.assertEqual(family.family_id, "")
        self.assertEqual(family.name, "")
        self.assertEqual(family.category, "")
        self.assertEqual(family.description, "")
        self.assertEqual(family.default_parameters, {})
        self.assertEqual(family.engineering_defaults, {})
        self.assertEqual(family.manufacturing_defaults, {})
        self.assertEqual(family.visual_defaults, {})
        self.assertEqual(family.commercial_defaults, {})
        self.assertEqual(family.metadata, {})

    def test_default_dictionaries_are_independent(self):
        first = ProductFamily()
        second = ProductFamily()

        first.default_parameters["width_mm"] = 600.0
        first.engineering_defaults["door_count"] = 2
        first.manufacturing_defaults["edge_banding_required"] = True
        first.visual_defaults["supports_overlay_preview"] = True
        first.commercial_defaults["markup_policy"] = "STANDARD"
        first.metadata["domain"] = "kitchen"

        self.assertEqual(second.default_parameters, {})
        self.assertEqual(second.engineering_defaults, {})
        self.assertEqual(second.manufacturing_defaults, {})
        self.assertEqual(second.visual_defaults, {})
        self.assertEqual(second.commercial_defaults, {})
        self.assertEqual(second.metadata, {})

    def test_no_engine_builder_renderer_manufacturing_cost_or_commercial_imports(self):
        source = inspect.getsource(product_family_module)
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

    def test_example_base_cabinet_family_can_be_represented_as_data_only(self):
        family = ProductFamily(
            family_id="BASE_CABINET",
            name="Base Cabinet",
            category="kitchen",
            description="Standard floor-mounted cabinet family.",
            default_parameters={
                "width_mm": 600.0,
                "height_mm": 720.0,
                "depth_mm": 580.0,
            },
            engineering_defaults={
                "door_count": 2,
                "shelf_count": 1,
                "has_back_panel": True,
            },
            manufacturing_defaults={
                "edge_banding_required": True,
                "toe_kick_required": True,
            },
            visual_defaults={
                "supports_overlay_preview": True,
                "default_finish": "MDF_18MM",
            },
            commercial_defaults={
                "pricing_group": "STANDARD_BASE",
            },
            metadata={
                "release_status": "foundation",
            },
        )

        self.assertEqual(family.family_id, "BASE_CABINET")
        self.assertEqual(family.name, "Base Cabinet")
        self.assertEqual(family.category, "kitchen")
        self.assertEqual(family.engineering_defaults["door_count"], 2)
        self.assertTrue(family.manufacturing_defaults["edge_banding_required"])
        self.assertEqual(family.visual_defaults["default_finish"], "MDF_18MM")
        self.assertEqual(family.commercial_defaults["pricing_group"], "STANDARD_BASE")
        self.assertEqual(family.metadata["release_status"], "foundation")

    def test_serialization_is_data_only(self):
        family = ProductFamily(
            family_id="WARDROBE",
            name="Wardrobe",
            category="storage",
            metadata={"variant_count": 0},
        )

        data = asdict(family)

        self.assertEqual(data["family_id"], "WARDROBE")
        self.assertEqual(data["name"], "Wardrobe")
        self.assertEqual(data["category"], "storage")
        self.assertEqual(data["metadata"], {"variant_count": 0})


if __name__ == "__main__":
    unittest.main()
