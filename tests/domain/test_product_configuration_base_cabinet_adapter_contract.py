import inspect
import unittest

import domain.product_configuration_base_cabinet_adapter as adapter_module
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.product_configuration import ProductConfiguration
from domain.product_configuration_base_cabinet_adapter import (
    adapt_product_configuration_to_base_cabinet_specification,
)


class TestProductConfigurationBaseCabinetAdapterContract(unittest.TestCase):
    def test_base_cabinet_product_configuration_maps_to_base_cabinet_specification(self):
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=900.0,
            height=800.0,
            depth=600.0,
            options={
                "door_count": 3,
                "shelf_count": 2,
                "has_back_panel": False,
                "edge_banding_required": False,
                "toe_kick_required": False,
                "hinge_family": "HEAVY_DUTY",
                "drawer_family": "DRAWER_STANDARD",
                "unknown_option": "ignored",
            },
        )

        specification = adapt_product_configuration_to_base_cabinet_specification(
            configuration
        )

        self.assertIsInstance(specification, BaseCabinetSpecification)
        self.assertEqual(specification.width_mm, 900.0)
        self.assertEqual(specification.height_mm, 800.0)
        self.assertEqual(specification.depth_mm, 600.0)
        self.assertEqual(specification.door_count, 3)
        self.assertEqual(specification.shelf_count, 2)
        self.assertFalse(specification.has_back_panel)
        self.assertFalse(specification.edge_banding_required)
        self.assertFalse(specification.toe_kick_required)
        self.assertEqual(specification.hinge_family, "HEAVY_DUTY")
        self.assertEqual(specification.drawer_family, "DRAWER_STANDARD")

    def test_lowercase_base_cabinet_is_accepted(self):
        configuration = ProductConfiguration(
            family_id="base_cabinet",
            width=600.0,
            height=720.0,
            depth=580.0,
        )

        specification = adapt_product_configuration_to_base_cabinet_specification(
            configuration
        )

        self.assertIsInstance(specification, BaseCabinetSpecification)
        self.assertEqual(specification.width_mm, 600.0)

    def test_unsupported_family_id_raises_value_error(self):
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=600.0,
            height=720.0,
            depth=350.0,
        )

        with self.assertRaises(ValueError):
            adapt_product_configuration_to_base_cabinet_specification(
                configuration
            )

    def test_material_is_not_forced_into_specification_if_unsupported(self):
        configuration = ProductConfiguration(
            family_id="BASE_CABINET",
            width=600.0,
            height=720.0,
            depth=580.0,
            material="PLYWOOD",
        )

        specification = adapt_product_configuration_to_base_cabinet_specification(
            configuration
        )

        self.assertFalse(hasattr(specification, "material"))
        self.assertEqual(specification, BaseCabinetSpecification())

    def test_adapter_does_not_import_application_engine_manufacturing_cost_or_commercial_modules(
        self,
    ):
        source = inspect.getsource(adapter_module)
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
        )
        for line in import_lines:
            for token in forbidden:
                self.assertNotIn(token, line)


if __name__ == "__main__":
    unittest.main()
