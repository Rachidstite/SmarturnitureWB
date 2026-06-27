import inspect
import unittest
from dataclasses import fields, is_dataclass

import manufacturing.operation_realizer as operation_realizer_module
from manufacturing.operation_realizer import (
    ManufacturingOperation,
    ManufacturingOperationRealizer,
    validate_manufacturing_operation_contract,
)
from manufacturing.operation_requirement import ManufacturingOperationRequirement
from manufacturing.operation_requirement_builder import (
    ManufacturingOperationRequirementBuilder,
)
from manufacturing.operation_vocabulary import OperationId


class TestOperationRealizerContract(unittest.TestCase):
    def setUp(self):
        self.builder = ManufacturingOperationRequirementBuilder()
        self.realizer = ManufacturingOperationRealizer()

    def test_realizer_converts_one_edge_band_requirement_into_one_operation(self):
        requirements = self.builder.build_for_panel("panel-1", needs_edge_band=True)
        operations = self.realizer.realize(requirements)
        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0].operation_id, OperationId.EDGE_BAND)

    def test_operation_instance_id_is_deterministic(self):
        requirement = self.builder.build_for_panel("panel-2", needs_edge_band=True)[0]
        operation = self.realizer.realize((requirement,))[0]
        self.assertEqual(
            operation.operation_instance_id,
            f"{requirement.requirement_id}::operation",
        )

    def test_operation_copies_operation_identity_fields_from_requirement(self):
        requirement = self.builder.build_for_door("door-1", needs_edge_band=True)[0]
        operation = self.realizer.realize((requirement,))[0]
        self.assertEqual(operation.operation_id, requirement.operation_id)
        self.assertEqual(operation.target_type, requirement.target_type)
        self.assertEqual(operation.target_id, requirement.target_id)

    def test_operation_preserves_source_requirement(self):
        requirement = self.builder.build_for_drawer("drawer-1", needs_slide=True)[0]
        operation = self.realizer.realize((requirement,))[0]
        self.assertIs(operation.source_requirement, requirement)

    def test_realizer_returns_tuple(self):
        requirements = self.builder.build_for_panel(
            "panel-3", needs_edge_band=True, needs_assembly_holes=True
        )
        operations = self.realizer.realize(requirements)
        self.assertIsInstance(operations, tuple)

    def test_realizer_validates_input_requirement(self):
        requirement = ManufacturingOperationRequirement(
            requirement_id="req-invalid",
            operation_id=OperationId.EDGE_BAND,
            target_type="",
            target_id="panel-invalid",
            reason="Needs banding.",
            source="ManufacturingModel",
        )
        with self.assertRaises(ValueError):
            self.realizer.realize((requirement,))

    def test_operation_metadata_rejects_forbidden_runtime_execution_keys(self):
        operation = ManufacturingOperation(
            operation_instance_id="req-1::operation",
            requirement_id="req-1",
            operation_id=OperationId.EDGE_BAND,
            target_type="Panel",
            target_id="panel-1",
            source_requirement=self.builder.build_for_panel("panel-1", needs_edge_band=True)[0],
            metadata={"job_id": "job-1"},
        )
        with self.assertRaises(ValueError):
            validate_manufacturing_operation_contract(operation)

    def test_manufacturing_operation_has_no_job_queue_machine_runtime_fields(self):
        field_names = {field.name for field in fields(ManufacturingOperation)}
        for forbidden in (
            "job_id",
            "queue_id",
            "machine_id",
            "runtime_status",
            "execution_status",
        ):
            self.assertNotIn(forbidden, field_names)

    def test_realizer_does_not_create_dependency_graph_or_execution_order(self):
        source = inspect.getsource(ManufacturingOperationRealizer)
        self.assertNotIn("dependency_graph", source)
        self.assertNotIn("execution_order", source)
        self.assertNotIn("order", source)

    def test_no_import_from_freecad(self):
        source = inspect.getsource(operation_realizer_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_import_from_production_package(self):
        source = inspect.getsource(operation_realizer_module)
        self.assertNotIn("ProductionPackage", source)
        self.assertNotIn("ManufacturingProductionPackage", source)

    def test_realized_operations_validate_contract(self):
        requirements = (
            self.builder.build_for_panel("panel-4", needs_edge_band=True)
            + self.builder.build_for_door("door-4", needs_hinges=True)
            + self.builder.build_for_drawer("drawer-4", needs_slide=True)
        )
        operations = self.realizer.realize(requirements)
        for operation in operations:
            validate_manufacturing_operation_contract(operation)
            self.assertIsInstance(operation, ManufacturingOperation)


if __name__ == "__main__":
    unittest.main()
