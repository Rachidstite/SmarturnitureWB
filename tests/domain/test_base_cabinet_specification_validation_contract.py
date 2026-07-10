import inspect
import unittest
from unittest.mock import patch

import domain.base_cabinet_specification_validation as validation_module
from core.material_manager import MaterialManager
from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_validation import (
    validate_base_cabinet_specification,
)
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from domain.diagnostics import ValidationReport
from engine.cabinet import Cabinet
from scene_graph.builder import SceneGraphBuilder
from types import SimpleNamespace


class TestBaseCabinetSpecificationValidationContract(unittest.TestCase):
    @staticmethod
    def _build_engineering_cabinet(specification: BaseCabinetSpecification) -> Cabinet:
        adapter_result = BaseCabinetSpecificationAdapter.adapt(specification)
        cabinet = Cabinet(params=adapter_result.cabinet_params)
        attach_base_cabinet_engineering_models(cabinet, specification)
        graph = SceneGraphBuilder(cabinet, MaterialManager()).build(None)
        cabinet.graph = graph
        cabinet.scene_graph = graph
        return cabinet

    def test_accepts_base_cabinet_specification(self):
        with patch.object(
            validation_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=self._build_engineering_cabinet(BaseCabinetSpecification()),
        ):
            report = validate_base_cabinet_specification(BaseCabinetSpecification())
        self.assertIsInstance(report, ValidationReport)

    def test_uses_adapter_path(self):
        cabinet = self._build_engineering_cabinet(BaseCabinetSpecification())
        with patch.object(
            BaseCabinetSpecificationAdapter,
            "adapt",
            wraps=BaseCabinetSpecificationAdapter.adapt,
        ) as adapt_spy, patch.object(
            validation_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=cabinet,
        ), patch(
            "domain.base_cabinet_specification_validation.CabinetConstraintValidator.validate_all",
            return_value=ValidationReport(),
        ) as validate_spy:
            validate_base_cabinet_specification(BaseCabinetSpecification())

        adapt_spy.assert_called_once()
        validate_spy.assert_called_once()

    def test_returns_existing_validation_result_type(self):
        with patch.object(
            validation_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=self._build_engineering_cabinet(BaseCabinetSpecification()),
        ):
            report = validate_base_cabinet_specification(BaseCabinetSpecification())
        self.assertIsInstance(report, ValidationReport)

    def test_width_height_depth_reach_validation_path(self):
        spec = BaseCabinetSpecification(width_mm=750.0, height_mm=900.0, depth_mm=620.0)

        captured = {}

        def fake_validate(self):
            captured["width"] = self.project.params.width
            captured["height"] = self.project.params.height
            captured["depth"] = self.project.params.depth
            captured["metadata"] = dict(self.project.metadata)
            return ValidationReport()

        with patch(
            "domain.base_cabinet_specification_validation.CabinetConstraintValidator.validate_all",
            new=fake_validate,
        ), patch.object(
            validation_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=self._build_engineering_cabinet(spec),
        ):
            validate_base_cabinet_specification(spec)

        self.assertEqual(captured["width"], 750.0)
        self.assertEqual(captured["height"], 900.0)
        self.assertEqual(captured["depth"], 620.0)

    def test_shelf_and_door_counts_reach_validation_through_geometry_shape(self):
        spec = BaseCabinetSpecification(
            door_count=3,
            shelf_count=2,
            has_back_panel=False,
            edge_banding_required=False,
            toe_kick_required=False,
            drawer_family="DRAWER_CUSTOM",
        )

        captured = {}

        def fake_validate(self):
            captured["params"] = self.project.params
            captured["metadata"] = dict(self.project.metadata)
            return ValidationReport()

        adapter_result = BaseCabinetSpecificationAdapter.adapt(spec)
        cabinet = SimpleNamespace(
            params=adapter_result.cabinet_params,
            graph=SimpleNamespace(physical_nodes=[], nodes=[]),
            scene_graph=SimpleNamespace(physical_nodes=[], nodes=[]),
        )

        with patch(
            "domain.base_cabinet_specification_validation.CabinetConstraintValidator.validate_all",
            new=fake_validate,
        ), patch.object(
            validation_module,
            "build_base_cabinet_engineering_cabinet",
            return_value=cabinet,
        ):
            validate_base_cabinet_specification(spec)

        params = captured["params"]
        self.assertFalse(hasattr(params, "door_count"))
        self.assertFalse(hasattr(params, "shelf_count"))
        self.assertFalse(hasattr(params, "drawer_family"))
        self.assertEqual(params.sec_count, 1)
        self.assertEqual(params.sec_data[0].door_count, 3)
        self.assertEqual(params.sec_data[0].shelves, 2)
        self.assertEqual(params.sec_data[0].doors, "Inset")
        self.assertEqual(params.back_panel_type, "NONE")
        self.assertEqual(captured["metadata"]["door_count"], 3)
        self.assertEqual(captured["metadata"]["shelf_count"], 2)
        self.assertFalse(captured["metadata"]["has_back_panel"])
        self.assertEqual(captured["metadata"]["drawer_family"], "DRAWER_CUSTOM")

    def test_has_back_panel_true_does_not_emit_missing_back_panel(self):
        spec = BaseCabinetSpecification(has_back_panel=True)
        cabinet = self._build_engineering_cabinet(spec)

        report = validate_base_cabinet_specification(spec, cabinet=cabinet)

        violation_codes = [violation.code for violation in report.violations]
        self.assertNotIn("MISSING_BACK_PANEL", violation_codes)

    def test_has_back_panel_false_keeps_missing_back_panel_warning(self):
        spec = BaseCabinetSpecification(has_back_panel=False)
        cabinet = self._build_engineering_cabinet(spec)

        report = validate_base_cabinet_specification(spec, cabinet=cabinet)

        violation_codes = [violation.code for violation in report.violations]
        self.assertIn("MISSING_BACK_PANEL", violation_codes)

    def test_existing_engineering_cabinet_scene_graph_is_used_for_validation(self):
        spec = BaseCabinetSpecification(has_back_panel=True)
        cabinet = self._build_engineering_cabinet(spec)
        captured = {}

        def fake_validate(self):
            captured["physical_nodes"] = list(self.project.graph.physical_nodes)
            return ValidationReport()

        with patch.object(
            validation_module,
            "build_base_cabinet_engineering_cabinet",
        ) as build_spy, patch(
            "domain.base_cabinet_specification_validation.CabinetConstraintValidator.validate_all",
            new=fake_validate,
        ):
            validate_base_cabinet_specification(spec, cabinet=cabinet)

        build_spy.assert_not_called()
        self.assertEqual(
            [node.identity.key for node in captured["physical_nodes"]],
            [node.identity.key for node in cabinet.scene_graph.all_nodes()],
        )
        self.assertEqual(
            captured["physical_nodes"][0].role,
            cabinet.scene_graph.all_nodes()[0].role.name,
        )

    def test_no_freecad_import(self):
        source = inspect.getsource(validation_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_runtime_build_execute_methods(self):
        source = inspect.getsource(validation_module)
        self.assertNotIn("def build", source)
        self.assertNotIn("def execute", source)
        self.assertNotIn("def run", source)


if __name__ == "__main__":
    unittest.main()
