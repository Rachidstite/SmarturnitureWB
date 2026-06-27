import inspect
import unittest
from dataclasses import fields, is_dataclass

import manufacturing.operation_instance as operation_instance_module
from manufacturing.operation_instance import (
    ManufacturingOperationInstance,
    validate_operation_instance_contract,
)
from manufacturing.operation_requirement_builder import (
    ManufacturingOperationRequirementBuilder,
)
from manufacturing.operation_realizer import ManufacturingOperationRealizer
from manufacturing.operation_vocabulary import OperationId


class TestOperationInstanceContract(unittest.TestCase):
    def setUp(self):
        self.requirement_builder = ManufacturingOperationRequirementBuilder()
        self.realizer = ManufacturingOperationRealizer()

    def _first_operation(self, requirements):
        return self.realizer.realize(requirements)[0]

    def test_instance_dataclass_contract(self):
        instance = ManufacturingOperationInstance(
            operation_instance_item_id="op-1::TOP",
            parent_operation_instance_id="op-1",
            operation_id=OperationId.EDGE_BAND,
            target_type="Panel",
            target_id="panel-1",
            instance_label="TOP",
        )
        self.assertTrue(is_dataclass(instance))
        self.assertEqual(
            [field.name for field in fields(ManufacturingOperationInstance)],
            [
                "operation_instance_item_id",
                "parent_operation_instance_id",
                "operation_id",
                "target_type",
                "target_id",
                "instance_label",
                "geometry_ref",
                "face",
                "metadata",
            ],
        )
        validate_operation_instance_contract(instance)

    def test_operation_instance_has_no_job_queue_machine_runtime_fields(self):
        field_names = {field.name for field in fields(ManufacturingOperationInstance)}
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
            "start_time",
            "end_time",
            "priority",
            "assigned_to",
        ):
            self.assertNotIn(forbidden, field_names)

    def test_instance_metadata_rejects_forbidden_runtime_execution_keys(self):
        instance = ManufacturingOperationInstance(
            operation_instance_item_id="op-1::TOP",
            parent_operation_instance_id="op-1",
            operation_id=OperationId.EDGE_BAND,
            target_type="Panel",
            target_id="panel-1",
            instance_label="TOP",
            metadata={"priority": 1},
        )
        with self.assertRaises(ValueError):
            validate_operation_instance_contract(instance)

    def test_no_import_from_freecad(self):
        source = inspect.getsource(operation_instance_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_import_from_production_package(self):
        source = inspect.getsource(operation_instance_module)
        self.assertNotIn("ProductionPackage", source)
        self.assertNotIn("ManufacturingProductionPackage", source)


if __name__ == "__main__":
    unittest.main()
