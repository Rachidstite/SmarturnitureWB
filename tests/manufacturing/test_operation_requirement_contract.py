import inspect
import unittest
from dataclasses import fields, is_dataclass
from typing import get_type_hints

import manufacturing.operation_requirement as operation_requirement_module
from manufacturing.operation_requirement import (
    ManufacturingOperationRequirement,
    validate_operation_requirement_contract,
)
from manufacturing.operation_vocabulary import OperationId


class TestOperationRequirementContract(unittest.TestCase):
    def test_requirement_can_be_created_for_edge_band_on_panel(self):
        requirement = ManufacturingOperationRequirement(
            requirement_id="req-001",
            operation_id=OperationId.EDGE_BAND,
            target_type="Panel",
            target_id="panel-001",
            reason="Expose edge needs banding.",
            source="ManufacturingModel",
        )
        self.assertTrue(is_dataclass(requirement))
        validate_operation_requirement_contract(requirement)

    def test_requirement_can_be_created_for_install_drawer_front_on_drawer(self):
        requirement = ManufacturingOperationRequirement(
            requirement_id="req-002",
            operation_id=OperationId.INSTALL_DRAWER_FRONT,
            target_type="Drawer",
            target_id="drawer-001",
            reason="Drawer front needs to be attached.",
            source="JoineryIntelligence",
        )
        validate_operation_requirement_contract(requirement)

    def test_requirement_operation_id_must_be_operation_id(self):
        requirement = ManufacturingOperationRequirement(
            requirement_id="req-003",
            operation_id=OperationId.EDGE_BAND,
            target_type="Panel",
            target_id="panel-002",
            reason="Edge banding required.",
            source="HardwareIntelligence",
        )
        self.assertEqual(get_type_hints(ManufacturingOperationRequirement)["operation_id"], OperationId)
        validate_operation_requirement_contract(requirement)
        invalid_requirement = ManufacturingOperationRequirement(
            requirement_id="req-003b",
            operation_id=OperationId.EDGE_BAND,
            target_type="Panel",
            target_id="panel-002",
            reason="Edge banding required.",
            source="HardwareIntelligence",
        )
        object.__setattr__(invalid_requirement, "operation_id", "EDGE_BAND")
        with self.assertRaises(TypeError):
            validate_operation_requirement_contract(invalid_requirement)

    def test_requirement_has_no_execution_fields(self):
        field_names = {field.name for field in fields(ManufacturingOperationRequirement)}
        for forbidden in (
            "machine_id",
            "worker_id",
            "operator_id",
            "job_id",
            "queue_id",
            "duration",
            "cost",
            "schedule",
            "station",
            "gcode",
            "tool_id",
            "runtime_status",
            "execution_status",
        ):
            self.assertNotIn(forbidden, field_names)

    def test_metadata_rejects_forbidden_execution_runtime_keys(self):
        requirement = ManufacturingOperationRequirement(
            requirement_id="req-004",
            operation_id=OperationId.EDGE_BAND,
            target_type="Panel",
            target_id="panel-003",
            reason="Edge banding required.",
            source="ManufacturingModel",
            metadata={"job_id": "job-1"},
        )
        with self.assertRaises(ValueError):
            validate_operation_requirement_contract(requirement)

    def test_requirement_id_is_not_treated_as_job_id(self):
        requirement = ManufacturingOperationRequirement(
            requirement_id="req-005",
            operation_id=OperationId.EDGE_BAND,
            target_type="Panel",
            target_id="panel-004",
            reason="Edge banding required.",
            source="ManufacturingModel",
        )
        self.assertFalse(hasattr(requirement, "job_id"))
        self.assertEqual(requirement.requirement_id, "req-005")

    def test_source_is_declarative_and_does_not_imply_execution(self):
        requirement = ManufacturingOperationRequirement(
            requirement_id="req-006",
            operation_id=OperationId.EDGE_BAND,
            target_type="Panel",
            target_id="panel-005",
            reason="Edge banding required.",
            source="ManufacturingModel",
        )
        self.assertIn(requirement.source, {"ManufacturingModel", "HardwareIntelligence", "JoineryIntelligence"})
        self.assertNotIn("execution", requirement.source.lower())
        self.assertNotIn("runtime", requirement.source.lower())

    def test_no_import_from_freecad_or_production_package(self):
        source = inspect.getsource(operation_requirement_module)
        self.assertNotIn("FreeCAD", source)
        self.assertNotIn("ProductionPackage", source)
        self.assertNotIn("ManufacturingProductionPackage", source)


if __name__ == "__main__":
    unittest.main()
