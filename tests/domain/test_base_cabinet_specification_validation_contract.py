import inspect
import unittest
from unittest.mock import patch

import domain.base_cabinet_specification_validation as validation_module
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_validation import (
    validate_base_cabinet_specification,
)
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from domain.diagnostics import ValidationReport


class TestBaseCabinetSpecificationValidationContract(unittest.TestCase):
    def test_accepts_base_cabinet_specification(self):
        report = validate_base_cabinet_specification(BaseCabinetSpecification())
        self.assertIsInstance(report, ValidationReport)

    def test_uses_adapter_path(self):
        with patch.object(
            BaseCabinetSpecificationAdapter,
            "adapt",
            wraps=BaseCabinetSpecificationAdapter.adapt,
        ) as adapt_spy, patch(
            "domain.base_cabinet_specification_validation.CabinetConstraintValidator.validate_all",
            return_value=ValidationReport(),
        ) as validate_spy:
            validate_base_cabinet_specification(BaseCabinetSpecification())

        adapt_spy.assert_called_once()
        validate_spy.assert_called_once()

    def test_returns_existing_validation_result_type(self):
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

        with patch(
            "domain.base_cabinet_specification_validation.CabinetConstraintValidator.validate_all",
            new=fake_validate,
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
        self.assertEqual(captured["metadata"]["door_count"], 3)
        self.assertEqual(captured["metadata"]["shelf_count"], 2)
        self.assertEqual(captured["metadata"]["drawer_family"], "DRAWER_CUSTOM")

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
