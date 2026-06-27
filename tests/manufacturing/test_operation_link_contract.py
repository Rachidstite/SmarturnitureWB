import inspect
import unittest
from dataclasses import fields, is_dataclass

import manufacturing.operation_link as operation_link_module
from manufacturing.operation_instance import ManufacturingOperationInstance
from manufacturing.operation_instantiator import ManufacturingOperationInstantiator
from manufacturing.operation_link import (
    ManufacturingOperationLink,
    validate_operation_link_contract,
)
from manufacturing.operation_realizer import ManufacturingOperationRealizer
from manufacturing.operation_requirement_builder import (
    ManufacturingOperationRequirementBuilder,
)
from manufacturing.operation_vocabulary import OperationId


class TestOperationLinkContract(unittest.TestCase):
    def setUp(self):
        self.requirement_builder = ManufacturingOperationRequirementBuilder()
        self.realizer = ManufacturingOperationRealizer()
        self.instantiator = ManufacturingOperationInstantiator()

    def _instance(self, requirement, labels, geometries, faces):
        operation = self.realizer.realize((requirement,))[0]
        return self.instantiator.instantiate(operation, labels, geometries, faces)

    def test_can_link_drill_hinge_cup_to_install_hinge(self):
        requirements = self.requirement_builder.build_for_door("door-1", needs_hinges=True)
        drill_hinge_cup = self.realizer.realize((requirements[1],))[0]
        install_hinge = self.realizer.realize((requirements[3],))[0]
        predecessor = self.instantiator.instantiate(drill_hinge_cup, ("HINGE_1",), ("geo-1",), ("face-1",))[0]
        successor = self.instantiator.instantiate(install_hinge, ("HINGE_1",), ("geo-2",), ("face-2",))[0]
        link = ManufacturingOperationLink(
            link_id=f"{predecessor.operation_instance_item_id}::REQUIRES_HARDWARE_PREPARATION::{successor.operation_instance_item_id}",
            predecessor_instance_id=predecessor.operation_instance_item_id,
            successor_instance_id=successor.operation_instance_item_id,
            relationship_type="REQUIRES_HARDWARE_PREPARATION",
            reason="Hinge installation requires hinge cup preparation.",
        )
        self.assertTrue(is_dataclass(link))
        validate_operation_link_contract(link)

    def test_can_link_drill_drawer_slide_holes_to_install_drawer_slide(self):
        requirement = self.requirement_builder.build_for_drawer("drawer-1", needs_slide=True)[0]
        operation = self.realizer.realize((requirement,))[0]
        predecessor = self.instantiator.instantiate(operation, ("LEFT",), ("geo-left",), ("face-left",))[0]
        install_requirement = self.requirement_builder.build_for_drawer("drawer-1", needs_slide=True)[1]
        install_operation = self.realizer.realize((install_requirement,))[0]
        successor = self.instantiator.instantiate(install_operation, ("LEFT",), ("geo-install",), ("face-install",))[0]
        link = ManufacturingOperationLink(
            link_id=f"{predecessor.operation_instance_item_id}::REQUIRES_HARDWARE_PREPARATION::{successor.operation_instance_item_id}",
            predecessor_instance_id=predecessor.operation_instance_item_id,
            successor_instance_id=successor.operation_instance_item_id,
            relationship_type="REQUIRES_HARDWARE_PREPARATION",
            reason="Slide installation requires prepared slide holes.",
        )
        validate_operation_link_contract(link)

    def test_link_id_is_deterministic(self):
        link = ManufacturingOperationLink(
            link_id="pre::REQUIRES_INSPECTION_INPUT::suc",
            predecessor_instance_id="pre",
            successor_instance_id="suc",
            relationship_type="REQUIRES_INSPECTION_INPUT",
            reason="Inspection follows prepared input.",
        )
        self.assertEqual(link.link_id, "pre::REQUIRES_INSPECTION_INPUT::suc")
        validate_operation_link_contract(link)

    def test_reject_empty_predecessor_successor(self):
        with self.assertRaises(ValueError):
            validate_operation_link_contract(
                ManufacturingOperationLink(
                    link_id="::REQUIRES_INSPECTION_INPUT::suc",
                    predecessor_instance_id="",
                    successor_instance_id="suc",
                    relationship_type="REQUIRES_INSPECTION_INPUT",
                    reason="Invalid",
                )
            )
        with self.assertRaises(ValueError):
            validate_operation_link_contract(
                ManufacturingOperationLink(
                    link_id="pre::REQUIRES_INSPECTION_INPUT::",
                    predecessor_instance_id="pre",
                    successor_instance_id="",
                    relationship_type="REQUIRES_INSPECTION_INPUT",
                    reason="Invalid",
                )
            )

    def test_reject_invalid_relationship_type(self):
        with self.assertRaises(ValueError):
            validate_operation_link_contract(
                ManufacturingOperationLink(
                    link_id="pre::INVALID::suc",
                    predecessor_instance_id="pre",
                    successor_instance_id="suc",
                    relationship_type="INVALID",
                    reason="Invalid",
                )
            )

    def test_reject_forbidden_metadata_keys(self):
        with self.assertRaises(ValueError):
            validate_operation_link_contract(
                ManufacturingOperationLink(
                    link_id="pre::REQUIRES_INSPECTION_INPUT::suc",
                    predecessor_instance_id="pre",
                    successor_instance_id="suc",
                    relationship_type="REQUIRES_INSPECTION_INPUT",
                    reason="Invalid",
                    metadata={"job_id": "job-1"},
                )
            )

    def test_operation_link_has_no_job_queue_machine_runtime_fields(self):
        field_names = {field.name for field in fields(ManufacturingOperationLink)}
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

    def test_no_graph_or_execution_logic_terms_in_implementation(self):
        source = inspect.getsource(operation_link_module)
        for term in ("dependencygraph", "workflowengine", "ordering algorithm"):
            self.assertNotIn(term, source.lower())

    def test_no_freecad_import(self):
        source = inspect.getsource(operation_link_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_manufacturing_production_package_import(self):
        source = inspect.getsource(operation_link_module)
        self.assertNotIn("ManufacturingProductionPackage", source)
        self.assertNotIn("ProductionPackage", source)


if __name__ == "__main__":
    unittest.main()
