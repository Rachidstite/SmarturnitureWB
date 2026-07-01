import ast
import inspect
import unittest

import domain.construction_resolver as resolver_module
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.construction_resolver import ConstructionResolver
from domain.furniture_construction_model import (
    BackPanelConstruction,
    BackPanelType,
    CabinetConstructionModel,
    CabinetConstructionSpecification,
    ConstructionMethod,
    HardwareConstruction,
    JoineryConstruction,
    PanelConstruction,
    ShelfConstruction,
    ShelfOwnership,
    ValidationSeverity,
)


class TestConstructionResolverDecisionContract(unittest.TestCase):
    def setUp(self):
        self.spec = BaseCabinetSpecification(
            width_mm=800.0,
            height_mm=720.0,
            depth_mm=560.0,
            door_count=2,
            shelf_count=1,
            has_back_panel=True,
            edge_banding_required=True,
            toe_kick_required=True,
            hinge_family="STANDARD_110",
            drawer_family="NONE",
        )
        self.model = ConstructionResolver.resolve(self.spec)

    def test_carcass_construction_decision(self):
        self.assertIsInstance(self.model, CabinetConstructionModel)
        self.assertIsInstance(self.model.specification, CabinetConstructionSpecification)
        self.assertEqual(len(self.model.panels), 4)
        self.assertIsInstance(self.model.panels[0], PanelConstruction)
        self.assertIsInstance(self.model.back_panel, BackPanelConstruction)
        self.assertIsInstance(self.model.joinery, JoineryConstruction)
        self.assertIsInstance(self.model.hardware, HardwareConstruction)
        self.assertEqual(
            {panel.role for panel in self.model.panels},
            {"SIDE_PANEL", "TOP_PANEL", "BOTTOM_PANEL"},
        )
        top = next(panel for panel in self.model.panels if panel.name == "Top")
        bottom = next(panel for panel in self.model.panels if panel.name == "Bottom")
        left = next(panel for panel in self.model.panels if panel.name == "Left Side")
        right = next(panel for panel in self.model.panels if panel.name == "Right Side")

        self.assertEqual(left.width_mm, 18.0)
        self.assertEqual(right.width_mm, 18.0)
        self.assertEqual(left.height_mm, self.spec.height_mm)
        self.assertEqual(right.height_mm, self.spec.height_mm)
        self.assertEqual(top.width_mm, self.spec.width_mm - 36.0)
        self.assertEqual(bottom.width_mm, self.spec.width_mm - 36.0)
        self.assertEqual(top.height_mm, 18.0)
        self.assertEqual(bottom.height_mm, 18.0)
        self.assertIn("between side panels", top.purpose)
        self.assertIn("between side panels", bottom.purpose)

    def test_material_thickness_decision(self):
        self.assertEqual(self.model.specification.material_thickness_mm, 18.0)
        self.assertEqual(self.model.specification.back_panel_thickness_mm, 3.0)

    def test_construction_method_decision(self):
        self.assertIs(
            self.model.specification.construction_method,
            ConstructionMethod.CONFIRMAT_OR_MINIFIX,
        )
        self.assertIs(
            self.model.joinery.method,
            ConstructionMethod.CONFIRMAT_OR_MINIFIX,
        )

    def test_back_panel_strategy_decision(self):
        self.assertIs(self.model.specification.back_panel_type, BackPanelType.GROOVED)
        self.assertEqual(self.model.back_panel.installation_mode, "GROOVED")
        self.assertEqual(self.model.back_panel.placement, "Inside rear groove behind side/top/bottom panels")
        self.assertIn("groove_seating", self.model.back_panel.allowed_details)

    def test_drawer_suppression_decision(self):
        self.assertEqual(self.model.specification.drawer_count, 0)
        self.assertEqual(len(self.model.doors), 0)

    def test_shelf_minimum_decision(self):
        self.assertEqual(self.model.specification.shelf_count, 1)
        self.assertEqual(len(self.model.shelves), 1)
        shelf = self.model.shelves[0]
        self.assertIsInstance(shelf, ShelfConstruction)
        self.assertEqual(shelf.shelf_pin_ownership, ShelfOwnership.SIDE_PANELS_ONLY)
        self.assertTrue(shelf.is_adjustable)
        self.assertEqual(shelf.fixed_or_adjustable, "ADJUSTABLE")

    def test_shelf_pin_manufacturability_hint_decision(self):
        self.assertEqual(self.model.hardware.shelf_pin_family, "SHELF_PIN_5MM")
        self.assertIn("shelf_pins", self.model.hardware.manufacturing_ready_details)
        self.assertEqual(
            self.model.shelves[0].shelf_pin_row_count,
            2,
        )

    def test_wall_mount_exclusion_decision(self):
        self.assertEqual(self.model.specification.wall_mount_count, 0)
        self.assertIn("wall_mount_hardware", self.model.hardware.prohibited_details)
        self.assertIn("wall_mount", self.model.disallowed_details)

    def test_hardware_policy_decision(self):
        self.assertEqual(self.model.hardware.hinge_family, self.spec.hinge_family)
        self.assertEqual(self.model.hardware.shelf_pin_family, "SHELF_PIN_5MM")
        self.assertEqual(
            self.model.hardware.joinery_hardware_family,
            "CONFIRMAT_OR_MINIFIX",
        )

    def test_validation_policy_decision(self):
        self.assertEqual(self.model.validation_issues, ())

        warning_model = ConstructionResolver.resolve(
            BaseCabinetSpecification(has_back_panel=False)
        )
        self.assertEqual(len(warning_model.validation_issues), 1)
        issue = warning_model.validation_issues[0]
        self.assertEqual(issue.code, "NO_BACK_PANEL")
        self.assertEqual(issue.severity, ValidationSeverity.WARNING)
        self.assertEqual(issue.target, "cabinet")

    def test_construction_model_boundary_decision(self):
        self.assertIsInstance(self.model, CabinetConstructionModel)
        for forbidden in (
            "scene_graph",
            "geometry",
            "manufacturing_package",
            "manufacturing_production_package",
            "product_family",
        ):
            self.assertFalse(hasattr(self.model, forbidden))

    def test_no_forbidden_imports(self):
        source = inspect.getsource(resolver_module)
        tree = ast.parse(source)
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)

        lowered = {module.lower() for module in imported_modules}
        for token in (
            "engine",
            "scene_graph",
            "manufacturing",
            "cost",
            "commercial",
            "application",
            "productfamily",
            "productconfiguration",
        ):
            self.assertFalse(
                any(token in module for module in lowered),
                msg=f"unexpected import token {token!r} found in {sorted(lowered)!r}",
            )


if __name__ == "__main__":
    unittest.main()
