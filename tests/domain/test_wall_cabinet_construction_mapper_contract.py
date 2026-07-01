import inspect
import unittest

import domain.wall_cabinet_construction_mapper as mapper_module
from domain.furniture_construction_model import CabinetConstructionModel
from domain.product_configuration import ProductConfiguration
from domain.product_configuration_wall_cabinet_mapper import (
    build_wall_cabinet_specification_from_product_configuration,
)
from domain.wall_cabinet_construction_mapper import (
    build_wall_cabinet_construction_model,
)
from domain.wall_cabinet_specification import WallCabinetSpecification


class TestWallCabinetConstructionMapperContract(unittest.TestCase):
    def test_mapper_returns_cabinet_construction_model(self):
        specification = WallCabinetSpecification()

        model = build_wall_cabinet_construction_model(specification)

        self.assertIsInstance(model, CabinetConstructionModel)

    def test_model_preserves_wall_cabinet_dimensions(self):
        specification = WallCabinetSpecification(
            width_mm=720.0,
            height_mm=900.0,
            depth_mm=380.0,
        )

        model = build_wall_cabinet_construction_model(specification)

        self.assertEqual(model.specification.width_mm, 720.0)
        self.assertEqual(model.specification.height_mm, 900.0)
        self.assertEqual(model.specification.depth_mm, 380.0)

    def test_model_has_wall_mount_count_greater_than_zero(self):
        model = build_wall_cabinet_construction_model(WallCabinetSpecification())

        self.assertGreater(model.specification.wall_mount_count, 0)

    def test_model_preserves_wall_mounting_evidence(self):
        specification = WallCabinetSpecification(
            wall_type="MASONRY",
            suspension_hardware_family="CONCEALED_BRACKET",
            max_load_kg=35.0,
            required_clearance_mm=45.0,
        )

        model = build_wall_cabinet_construction_model(specification)

        self.assertEqual(model.specification.wall_mount_count, 1)
        self.assertEqual(model.hardware.hinge_family, specification.hinge_family)
        self.assertEqual(
            model.hardware.joinery_hardware_family,
            "CONFIRMAT_OR_MINIFIX",
        )
        self.assertIn("wall_mount_hardware", model.hardware.manufacturing_ready_details)
        self.assertIn("wall_mount", model.allowed_details)
        self.assertEqual(len(model.shelves), max(specification.shelf_count, 1))

    def test_model_does_not_contain_geometry(self):
        model = build_wall_cabinet_construction_model(WallCabinetSpecification())

        for forbidden in ("geometry", "scene_graph", "manufacturing_package"):
            self.assertFalse(hasattr(model, forbidden))

    def test_mapper_does_not_import_forbidden_modules(self):
        source = inspect.getsource(mapper_module)
        import_lines = [
            line.strip()
            for line in source.splitlines()
            if line.strip().startswith("import ") or line.strip().startswith("from ")
        ]
        for token in (
            "constructionresolver",
            "cabinetbuilder",
            "geometryengine",
            "scene_graph",
            "manufacturing",
            "cost",
            "commercial",
            "application",
        ):
            for line in import_lines:
                self.assertNotIn(token, line.lower())

    def test_repeated_calls_are_deterministic(self):
        configuration = ProductConfiguration(
            family_id="WALL_CABINET",
            width=680.0,
            height=760.0,
            depth=360.0,
            options={"door_count": 2, "shelf_count": 2},
        )

        first = build_wall_cabinet_construction_model(
            build_wall_cabinet_specification_from_product_configuration(
                configuration
            )
        )
        second = build_wall_cabinet_construction_model(
            build_wall_cabinet_specification_from_product_configuration(
                configuration
            )
        )

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
