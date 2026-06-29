import ast
import inspect
import json
import unittest
from dataclasses import fields, is_dataclass

import domain.furniture_construction_model as construction_module
from domain.furniture_construction_model import (
    BackPanelConstruction,
    BackPanelType,
    CabinetConstructionModel,
    CabinetConstructionSpecification,
    ConstructionMethod,
    ConstructionValidationIssue,
    DoorConstruction,
    HingeSide,
    HardwareConstruction,
    JoineryConstruction,
    PanelConstruction,
    ShelfConstruction,
    ShelfOwnership,
)


class TestFurnitureConstructionModelContract(unittest.TestCase):
    def setUp(self):
        self.model = CabinetConstructionModel.reference_base_cabinet()

    def test_reference_cabinet_has_correct_dimensions(self):
        spec = self.model.specification

        self.assertEqual(spec.width_mm, 800.0)
        self.assertEqual(spec.height_mm, 720.0)
        self.assertEqual(spec.depth_mm, 560.0)
        self.assertEqual(spec.material_thickness_mm, 18.0)

    def test_grooved_back_panel_is_represented_correctly(self):
        back = self.model.back_panel

        self.assertIsInstance(back, BackPanelConstruction)
        self.assertEqual(back.panel.thickness_mm, 3.0)
        self.assertEqual(back.panel.role, "BACK_PANEL")
        self.assertEqual(back.installation_mode, "GROOVED")
        self.assertEqual(back.placement, "Inside rear groove behind side/top/bottom panels")
        self.assertIn("groove_seating", back.allowed_details)
        self.assertNotIn("floating_back_panel", back.allowed_details)

    def test_two_doors_have_opposite_hinge_sides(self):
        self.assertEqual(len(self.model.doors), 2)
        left_door, right_door = self.model.doors

        self.assertIsInstance(left_door, DoorConstruction)
        self.assertIsInstance(right_door, DoorConstruction)
        self.assertEqual(left_door.hinge_side, HingeSide.LEFT)
        self.assertEqual(right_door.hinge_side, HingeSide.RIGHT)
        self.assertEqual(left_door.hinge_count, 2)
        self.assertEqual(right_door.hinge_count, 2)

    def test_shelf_is_adjustable(self):
        self.assertEqual(len(self.model.shelves), 1)
        shelf = self.model.shelves[0]

        self.assertIsInstance(shelf, ShelfConstruction)
        self.assertTrue(shelf.is_adjustable)
        self.assertEqual(shelf.fixed_or_adjustable, "ADJUSTABLE")
        self.assertEqual(shelf.shelf_pin_ownership, ShelfOwnership.SIDE_PANELS_ONLY)

    def test_shelf_construction_does_not_own_coordinates(self):
        self.assertNotIn(
            "position_mm",
            [field.name for field in fields(ShelfConstruction)],
        )

    def test_shelf_pin_ownership_is_side_panels_only(self):
        shelf = self.model.shelves[0]

        self.assertEqual(shelf.shelf_pin_ownership.value, "SIDE_PANELS_ONLY")

    def test_joinery_method_is_explicit(self):
        self.assertIsInstance(self.model.joinery, JoineryConstruction)
        self.assertEqual(
            self.model.joinery.method,
            ConstructionMethod.CONFIRMAT_OR_MINIFIX,
        )
        self.assertIn("confirmat_joinery", self.model.joinery.visible_details)
        self.assertIn("minifix_joinery", self.model.joinery.visible_details)

    def test_no_drawer_construction_exists(self):
        spec = self.model.specification

        self.assertEqual(spec.drawer_count, 0)
        self.assertEqual(
            [panel.role for panel in self.model.panels if "DRAWER" in panel.role],
            [],
        )

    def test_model_is_serialization_friendly(self):
        data = self.model.to_dict()
        encoded = json.dumps(data)

        self.assertIn('"width_mm": 800.0', encoded)
        self.assertEqual(data["specification"]["back_panel_type"], "GROOVED")
        self.assertEqual(data["doors"][0]["hinge_side"], "LEFT")
        self.assertEqual(data["shelves"][0]["shelf_pin_ownership"], "SIDE_PANELS_ONLY")

    def test_model_is_dataclass(self):
        self.assertTrue(is_dataclass(CabinetConstructionModel))
        self.assertEqual(
            [field.name for field in fields(CabinetConstructionModel)],
            [
                "specification",
                "panels",
                "back_panel",
                "doors",
                "shelves",
                "joinery",
                "hardware",
                "validation_issues",
                "allowed_details",
                "disallowed_details",
            ],
        )

    def test_no_freecad_import(self):
        source = inspect.getsource(construction_module)
        tree = ast.parse(source)
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)

        lowered = {module.lower() for module in imported_modules}
        self.assertFalse(any("freecad" in module for module in lowered))

    def test_no_renderer_import(self):
        source = inspect.getsource(construction_module)
        tree = ast.parse(source)
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)

        lowered = {module.lower() for module in imported_modules}
        self.assertFalse(any("renderer" in module for module in lowered))

    def test_validation_issues_are_explicit(self):
        issues = self.model.validation_issues

        self.assertTrue(all(isinstance(issue, ConstructionValidationIssue) for issue in issues))
        self.assertEqual({issue.code for issue in issues}, {"NO_DRAWERS", "NO_WALL_MOUNT"})


if __name__ == "__main__":
    unittest.main()
