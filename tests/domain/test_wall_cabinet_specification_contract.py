import inspect
import unittest
from dataclasses import fields, is_dataclass

import domain.wall_cabinet_specification as wall_cabinet_spec_module
from domain.wall_cabinet_specification import WallCabinetSpecification


class TestWallCabinetSpecificationContract(unittest.TestCase):
    def test_valid_wall_cabinet_spec_preserves_dimensions_and_wall_mounting_fields(self):
        spec = WallCabinetSpecification(
            width_mm=700.0,
            height_mm=800.0,
            depth_mm=360.0,
            door_count=2,
            shelf_count=3,
            has_back_panel=False,
            edge_banding_required=True,
            hinge_family="STANDARD_110",
            suspension_hardware_family="CONCEALED_BRACKET",
            wall_type="TIMBER_STUD",
            max_load_kg=30.0,
            required_clearance_mm=40.0,
        )

        self.assertTrue(is_dataclass(WallCabinetSpecification))
        self.assertEqual(
            [field.name for field in fields(WallCabinetSpecification)],
            [
                "width_mm",
                "height_mm",
                "depth_mm",
                "door_count",
                "shelf_count",
                "has_back_panel",
                "edge_banding_required",
                "hinge_family",
                "suspension_hardware_family",
                "wall_type",
                "max_load_kg",
                "required_clearance_mm",
            ],
        )
        self.assertEqual(spec.width_mm, 700.0)
        self.assertEqual(spec.height_mm, 800.0)
        self.assertEqual(spec.depth_mm, 360.0)
        self.assertEqual(spec.door_count, 2)
        self.assertEqual(spec.shelf_count, 3)
        self.assertFalse(spec.has_back_panel)
        self.assertTrue(spec.edge_banding_required)
        self.assertEqual(spec.hinge_family, "STANDARD_110")
        self.assertEqual(spec.suspension_hardware_family, "CONCEALED_BRACKET")
        self.assertEqual(spec.wall_type, "TIMBER_STUD")
        self.assertEqual(spec.max_load_kg, 30.0)
        self.assertEqual(spec.required_clearance_mm, 40.0)

    def test_invalid_dimensions_raise_value_error(self):
        with self.assertRaises(ValueError):
            WallCabinetSpecification(width_mm=0)
        with self.assertRaises(ValueError):
            WallCabinetSpecification(height_mm=0)
        with self.assertRaises(ValueError):
            WallCabinetSpecification(depth_mm=0)

    def test_invalid_negative_door_or_shelf_counts_raise_value_error(self):
        with self.assertRaises(ValueError):
            WallCabinetSpecification(door_count=-1)
        with self.assertRaises(ValueError):
            WallCabinetSpecification(shelf_count=-1)

    def test_missing_hinge_suspension_or_wall_type_raises_value_error(self):
        with self.assertRaises(ValueError):
            WallCabinetSpecification(hinge_family="")
        with self.assertRaises(ValueError):
            WallCabinetSpecification(suspension_hardware_family="")
        with self.assertRaises(ValueError):
            WallCabinetSpecification(wall_type="")

    def test_no_base_specific_fields_exist(self):
        spec_fields = {field.name for field in fields(WallCabinetSpecification)}
        self.assertNotIn("toe_kick_required", spec_fields)
        self.assertNotIn("base_height", spec_fields)
        self.assertNotIn("plinth", spec_fields)
        self.assertNotIn("floor_support", spec_fields)

    def test_no_forbidden_runtime_imports(self):
        source = inspect.getsource(wall_cabinet_spec_module)
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
