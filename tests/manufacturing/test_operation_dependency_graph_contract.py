import inspect
import unittest
from dataclasses import fields, is_dataclass

import manufacturing.operation_dependency_graph as operation_dependency_graph_module
from manufacturing.operation_dependency_graph import (
    ManufacturingOperationDependencyGraph,
    ManufacturingOperationDependencyGraphBuilder,
    validate_operation_dependency_graph_contract,
)
from manufacturing.operation_instantiator import ManufacturingOperationInstantiator
from manufacturing.operation_link import ManufacturingOperationLink
from manufacturing.operation_realizer import ManufacturingOperationRealizer
from manufacturing.operation_requirement_builder import (
    ManufacturingOperationRequirementBuilder,
)
from manufacturing.operation_vocabulary import OperationId


class TestOperationDependencyGraphContract(unittest.TestCase):
    def setUp(self):
        self.requirement_builder = ManufacturingOperationRequirementBuilder()
        self.realizer = ManufacturingOperationRealizer()
        self.instantiator = ManufacturingOperationInstantiator()
        self.builder = ManufacturingOperationDependencyGraphBuilder()

    def _build_pair(self):
        door_requirements = self.requirement_builder.build_for_door("door-1", needs_hinges=True)
        drill_hinge_cup = self.realizer.realize((door_requirements[1],))[0]
        install_hinge = self.realizer.realize((door_requirements[3],))[0]
        predecessor = self.instantiator.instantiate(
            drill_hinge_cup, ("HINGE_1",), ("geo-1",), ("face-1",)
        )[0]
        successor = self.instantiator.instantiate(
            install_hinge, ("HINGE_1",), ("geo-2",), ("face-2",)
        )[0]
        link = ManufacturingOperationLink(
            link_id=f"{predecessor.operation_instance_item_id}::REQUIRES_HARDWARE_PREPARATION::{successor.operation_instance_item_id}",
            predecessor_instance_id=predecessor.operation_instance_item_id,
            successor_instance_id=successor.operation_instance_item_id,
            relationship_type="REQUIRES_HARDWARE_PREPARATION",
            reason="Hinge installation requires hinge preparation.",
        )
        return predecessor, successor, link

    def test_build_graph_from_two_operation_instances_and_one_link(self):
        predecessor, successor, link = self._build_pair()
        graph = self.builder.build((predecessor, successor), (link,))
        self.assertTrue(is_dataclass(graph))
        self.assertEqual(graph.instance_ids, (predecessor.operation_instance_item_id, successor.operation_instance_item_id))
        self.assertEqual(graph.links, (link,))
        validate_operation_dependency_graph_contract(graph)

    def test_adjacency_contains_predecessor_to_successor(self):
        predecessor, successor, link = self._build_pair()
        graph = self.builder.build((predecessor, successor), (link,))
        self.assertEqual(graph.adjacency[predecessor.operation_instance_item_id], (successor.operation_instance_item_id,))

    def test_reverse_adjacency_contains_successor_to_predecessor(self):
        predecessor, successor, link = self._build_pair()
        graph = self.builder.build((predecessor, successor), (link,))
        self.assertEqual(graph.reverse_adjacency[successor.operation_instance_item_id], (predecessor.operation_instance_item_id,))

    def test_reject_link_with_missing_predecessor(self):
        _, successor, link = self._build_pair()
        invalid = ManufacturingOperationLink(
            link_id=f"missing::REQUIRES_HARDWARE_PREPARATION::{successor.operation_instance_item_id}",
            predecessor_instance_id="missing",
            successor_instance_id=successor.operation_instance_item_id,
            relationship_type=link.relationship_type,
            reason=link.reason,
        )
        with self.assertRaises(ValueError):
            self.builder.build((successor,), (invalid,))

    def test_reject_link_with_missing_successor(self):
        predecessor, _, link = self._build_pair()
        invalid = ManufacturingOperationLink(
            link_id=f"{predecessor.operation_instance_item_id}::REQUIRES_HARDWARE_PREPARATION::missing",
            predecessor_instance_id=predecessor.operation_instance_item_id,
            successor_instance_id="missing",
            relationship_type=link.relationship_type,
            reason=link.reason,
        )
        with self.assertRaises(ValueError):
            self.builder.build((predecessor,), (invalid,))

    def test_graph_does_not_infer_missing_links(self):
        predecessor, successor, link = self._build_pair()
        graph = self.builder.build((predecessor, successor), ())
        self.assertEqual(graph.links, ())
        self.assertEqual(graph.adjacency[predecessor.operation_instance_item_id], ())
        self.assertEqual(graph.reverse_adjacency[successor.operation_instance_item_id], ())

    def test_graph_does_not_add_missing_instances(self):
        predecessor, successor, link = self._build_pair()
        graph = self.builder.build((predecessor, successor), (link,))
        self.assertEqual(graph.instance_ids, (predecessor.operation_instance_item_id, successor.operation_instance_item_id))
        self.assertNotIn("missing", graph.instance_ids)

    def test_graph_has_no_job_queue_machine_runtime_fields(self):
        field_names = {field.name for field in fields(ManufacturingOperationDependencyGraph)}
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

    def test_graph_metadata_rejects_forbidden_runtime_execution_keys(self):
        graph = ManufacturingOperationDependencyGraph(
            instance_ids=("a",),
            links=(),
            adjacency={"a": ()},
            reverse_adjacency={"a": ()},
            metadata={"job_id": "job-1"},
        )
        with self.assertRaises(ValueError):
            validate_operation_dependency_graph_contract(graph)

    def test_no_freecad_import(self):
        source = inspect.getsource(operation_dependency_graph_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_manufacturing_production_package_import(self):
        source = inspect.getsource(operation_dependency_graph_module)
        self.assertNotIn("ManufacturingProductionPackage", source)
        self.assertNotIn("ProductionPackage", source)

    def test_no_execution_planning_terms_in_implementation(self):
        source = inspect.getsource(operation_dependency_graph_module).lower()
        for term in ("workflow", "runtime", "job", "queue", "machine", "cnc", "ordering", "scheduling"):
            self.assertNotIn(term, source)


if __name__ == "__main__":
    unittest.main()
