import inspect
import unittest

import domain.product_configuration_wall_cabinet_mapper as mapper_module
from domain.product_configuration import ProductConfiguration
from domain.product_configuration_wall_cabinet_mapper import (
    build_wall_cabinet_specification_from_product_configuration,
)
from domain.wall_cabinet_specification import WallCabinetSpecification


class TestProductConfigurationWallCabinetMapperContract(unittest.TestCase):
    def test_every_product_configuration_field_maps_correctly(self):
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=750.0,
            height=900.0,
            depth=360.0,
            material="PLYWOOD",
            options={
                "door_count": 3,
                "shelf_count": 4,
                "has_back_panel": False,
                "edge_banding_required": False,
                "hinge_family": "STANDARD_95",
                "suspension_hardware_family": "CONCEALED_BRACKET",
                "wall_type": "MASONRY",
                "max_load_kg": 40.0,
                "required_clearance_mm": 55.0,
            },
            metadata={"source": "unit-test"},
        )

        specification = build_wall_cabinet_specification_from_product_configuration(
            configuration
        )

        self.assertIsInstance(specification, WallCabinetSpecification)
        self.assertEqual(specification.width_mm, configuration.width)
        self.assertEqual(specification.height_mm, configuration.height)
        self.assertEqual(specification.depth_mm, configuration.depth)
        self.assertEqual(specification.door_count, 3)
        self.assertEqual(specification.shelf_count, 4)
        self.assertFalse(specification.has_back_panel)
        self.assertFalse(specification.edge_banding_required)
        self.assertEqual(specification.hinge_family, "STANDARD_95")
        self.assertEqual(specification.suspension_hardware_family, "CONCEALED_BRACKET")
        self.assertEqual(specification.wall_type, "MASONRY")
        self.assertEqual(specification.max_load_kg, 40.0)
        self.assertEqual(specification.required_clearance_mm, 55.0)

    def test_wall_specific_fields_are_preserved_with_defaults(self):
        configuration = ProductConfiguration(
            family_id="wall_cabinet",
            width=600.0,
            height=720.0,
            depth=350.0,
        )

        specification = build_wall_cabinet_specification_from_product_configuration(
            configuration
        )

        self.assertEqual(specification.hinge_family, WallCabinetSpecification().hinge_family)
        self.assertEqual(
            specification.suspension_hardware_family,
            WallCabinetSpecification().suspension_hardware_family,
        )
        self.assertEqual(specification.wall_type, WallCabinetSpecification().wall_type)
        self.assertEqual(specification.max_load_kg, WallCabinetSpecification().max_load_kg)
        self.assertEqual(
            specification.required_clearance_mm,
            WallCabinetSpecification().required_clearance_mm,
        )

    def test_mapper_produces_wall_cabinet_specification_only(self):
        specification = build_wall_cabinet_specification_from_product_configuration(
            ProductConfiguration(
                family_id="WALL_CABINET",
                width=600.0,
                height=720.0,
                depth=350.0,
            )
        )

        self.assertIsInstance(specification, WallCabinetSpecification)
        self.assertFalse(hasattr(specification, "cabinet"))
        self.assertFalse(hasattr(specification, "engineering_model"))

    def test_mapper_performs_no_engineering_routing_geometry_or_manufacturing(self):
        source = inspect.getsource(mapper_module)
        lowered = source.lower()
        for token in (
            "engineering",
            "constructionresolver",
            "cabinetbuilder",
            "geometryengine",
            "scene_graph",
            "manufacturing",
            "commercial",
            "application",
        ):
            self.assertNotIn(token, lowered)

    def test_repeated_calls_are_deterministic(self):
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=620.0,
            height=740.0,
            depth=360.0,
            options={"door_count": 2, "shelf_count": 3},
        )

        first = build_wall_cabinet_specification_from_product_configuration(
            configuration
        )
        second = build_wall_cabinet_specification_from_product_configuration(
            configuration
        )

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
