import inspect
import unittest

import domain.product_configuration_family_classifier as classifier_module
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.product_configuration import ProductConfiguration
from domain.product_configuration_base_cabinet_adapter import (
    adapt_product_configuration_to_base_cabinet_specification,
)
from domain.product_configuration_family_classifier import (
    ProductConfigurationFamilyClassification,
    classify_product_configuration_family,
)


class TestProductConfigurationFamilyClassifierContract(unittest.TestCase):
    def test_base_cabinet_is_classified_as_executable_through_base_cabinet_path(
        self,
    ):
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=600.0,
            height=720.0,
            depth=580.0,
        )

        classification = classify_product_configuration_family(configuration)

        self.assertIsInstance(
            classification,
            ProductConfigurationFamilyClassification,
        )
        self.assertTrue(classification.executable_family)
        self.assertEqual(classification.engineering_path, "base_cabinet")
        self.assertIn("executable", classification.reason.lower())

    def test_lowercase_base_cabinet_behaves_the_same(self):
        configuration = ProductConfiguration(
            family_id="base_cabinet",
            width=600.0,
            height=720.0,
            depth=580.0,
        )

        classification = classify_product_configuration_family(configuration)

        self.assertTrue(classification.executable_family)
        self.assertEqual(classification.engineering_path, "base_cabinet")

    def test_wall_cabinet_is_recognized_but_catalog_only(self):
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=600.0,
            height=720.0,
            depth=350.0,
        )

        classification = classify_product_configuration_family(configuration)

        self.assertFalse(classification.executable_family)
        self.assertIsNone(classification.engineering_path)
        self.assertIn("catalog-only", classification.reason.lower())

    def test_lowercase_wall_cabinet_behaves_the_same(self):
        configuration = ProductConfiguration(
            family_id="wall_cabinet",
            width=600.0,
            height=720.0,
            depth=350.0,
        )

        classification = classify_product_configuration_family(configuration)

        self.assertFalse(classification.executable_family)
        self.assertIsNone(classification.engineering_path)
        self.assertIn("catalog-only", classification.reason.lower())

    def test_tall_cabinet_is_recognized_but_catalog_only(self):
        configuration = ProductConfiguration(
            family_id="TALL_CABINET",
            width=600.0,
            height=2100.0,
            depth=580.0,
        )

        classification = classify_product_configuration_family(configuration)

        self.assertFalse(classification.executable_family)
        self.assertIsNone(classification.engineering_path)
        self.assertIn("catalog-only", classification.reason.lower())

    def test_unknown_family_is_classified_as_unknown(self):
        configuration = ProductConfiguration(
            family_id="WARDROBE",
            width=900.0,
            height=2100.0,
            depth=600.0,
        )

        classification = classify_product_configuration_family(configuration)

        self.assertFalse(classification.executable_family)
        self.assertIsNone(classification.engineering_path)
        self.assertIn("unknown family", classification.reason.lower())

    def test_classifier_does_not_import_application_engine_manufacturing_cost_or_commercial_modules(
        self,
    ):
        source = inspect.getsource(classifier_module)
        import_lines = [
            line.strip()
            for line in source.splitlines()
            if line.strip().startswith("import ") or line.strip().startswith("from ")
        ]

        forbidden = (
            "application",
            "engine",
            "manufacturing",
            "cost",
            "commercial",
            "workflow",
            "pipeline",
        )
        for line in import_lines:
            for token in forbidden:
                self.assertNotIn(token, line)

    def test_existing_base_cabinet_adapter_behavior_remains_unchanged(self):
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=600.0,
            height=720.0,
            depth=580.0,
            options={
                "door_count": 2,
                "shelf_count": 1,
                "has_back_panel": True,
                "edge_banding_required": True,
                "toe_kick_required": True,
                "hinge_family": "STANDARD_110",
                "drawer_family": "NONE",
            },
        )

        specification = adapt_product_configuration_to_base_cabinet_specification(
            configuration
        )

        self.assertIsInstance(specification, BaseCabinetSpecification)
        self.assertEqual(specification.width_mm, 600.0)
        self.assertEqual(specification.height_mm, 720.0)
        self.assertEqual(specification.depth_mm, 580.0)
        self.assertEqual(specification.door_count, 2)
        self.assertEqual(specification.shelf_count, 1)
        self.assertTrue(specification.has_back_panel)
        self.assertTrue(specification.edge_banding_required)
        self.assertTrue(specification.toe_kick_required)
        self.assertEqual(specification.hinge_family, "STANDARD_110")
        self.assertEqual(specification.drawer_family, "NONE")


if __name__ == "__main__":
    unittest.main()
