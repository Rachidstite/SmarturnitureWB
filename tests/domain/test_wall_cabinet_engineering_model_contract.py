import inspect
import unittest
from dataclasses import fields, is_dataclass

import domain.wall_cabinet_engineering_model as wall_model_module
from domain.wall_cabinet_engineering_model import WallCabinetEngineeringModel
from domain.wall_cabinet_specification import WallCabinetSpecification


class TestWallCabinetEngineeringModelContract(unittest.TestCase):
    def test_model_preserves_specification_fields(self):
        specification = WallCabinetSpecification(
            width_mm=700.0,
            height_mm=800.0,
            depth_mm=360.0,
            door_count=2,
            shelf_count=3,
            has_back_panel=False,
            edge_banding_required=True,
            hinge_family="STANDARD_110",
            suspension_hardware_family="CONCEALED_BRACKET",
            wall_type="MASONRY",
            max_load_kg=30.0,
            required_clearance_mm=40.0,
        )

        model = WallCabinetEngineeringModel(
            specification=specification,
        )

        self.assertTrue(is_dataclass(WallCabinetEngineeringModel))
        self.assertEqual(
            [field.name for field in fields(WallCabinetEngineeringModel)],
            [
                "specification",
                "mounting_type",
                "support_strategy",
                "executable_geometry",
            ],
        )
        self.assertIs(model.specification, specification)
        self.assertEqual(model.has_back_panel, specification.has_back_panel)
        self.assertEqual(model.door_count, specification.door_count)
        self.assertEqual(model.shelf_count, specification.shelf_count)
        self.assertEqual(
            model.suspension_hardware_family,
            specification.suspension_hardware_family,
        )
        self.assertEqual(model.wall_type, specification.wall_type)
        self.assertEqual(model.max_load_kg, specification.max_load_kg)
        self.assertEqual(model.required_clearance_mm, specification.required_clearance_mm)

    def test_model_exposes_wall_mounting_support_semantics(self):
        model = WallCabinetEngineeringModel(
            specification=WallCabinetSpecification(),
        )

        self.assertEqual(model.mounting_type, "wall")
        self.assertEqual(model.support_strategy, "wall_mounted")

    def test_executable_geometry_is_false(self):
        model = WallCabinetEngineeringModel(
            specification=WallCabinetSpecification(),
        )

        self.assertFalse(model.executable_geometry)

    def test_no_base_specific_fields_exist(self):
        model_fields = {field.name for field in fields(WallCabinetEngineeringModel)}
        self.assertNotIn("toe_kick_required", model_fields)
        self.assertNotIn("base_height", model_fields)
        self.assertNotIn("plinth", model_fields)
        self.assertNotIn("floor_support", model_fields)
        self.assertNotIn("has_back_panel", model_fields)
        self.assertNotIn("door_count", model_fields)
        self.assertNotIn("shelf_count", model_fields)
        self.assertNotIn("suspension_hardware_family", model_fields)
        self.assertNotIn("wall_type", model_fields)
        self.assertNotIn("max_load_kg", model_fields)
        self.assertNotIn("required_clearance_mm", model_fields)

    def test_no_base_specific_properties_exist(self):
        self.assertFalse(hasattr(WallCabinetEngineeringModel, "toe_kick_required"))
        self.assertFalse(hasattr(WallCabinetEngineeringModel, "base_height"))
        self.assertFalse(hasattr(WallCabinetEngineeringModel, "plinth"))
        self.assertFalse(hasattr(WallCabinetEngineeringModel, "floor_support"))

    def test_no_forbidden_runtime_imports(self):
        source = inspect.getsource(wall_model_module)
        lowered = source.lower()
        for token in (
            "cabinetbuilder",
            "constructionresolver",
            "manufacturing",
            "cost",
            "commercial",
            "application",
        ):
            self.assertNotIn(token, lowered)


if __name__ == "__main__":
    unittest.main()
