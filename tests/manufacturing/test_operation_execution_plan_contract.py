import inspect
import unittest
from dataclasses import fields, is_dataclass

import manufacturing.operation_execution_plan as operation_execution_plan_module
from manufacturing.operation_dependency_graph import ManufacturingOperationDependencyGraphBuilder
from manufacturing.operation_execution_plan import (
    ManufacturingLogicalExecutionPlan,
    ManufacturingLogicalExecutionPlanBuilder,
    validate_logical_execution_plan_contract,
)
from manufacturing.operation_instantiator import ManufacturingOperationInstantiator
from manufacturing.operation_link import ManufacturingOperationLink
from manufacturing.operation_realizer import ManufacturingOperationRealizer
from manufacturing.operation_requirement_builder import (
    ManufacturingOperationRequirementBuilder,
)


class TestOperationExecutionPlanContract(unittest.TestCase):
    def setUp(self):
        self.requirement_builder = ManufacturingOperationRequirementBuilder()
        self.realizer = ManufacturingOperationRealizer()
        self.instantiator = ManufacturingOperationInstantiator()
        self.graph_builder = ManufacturingOperationDependencyGraphBuilder()
        self.plan_builder = ManufacturingLogicalExecutionPlanBuilder()

    def _build_graph_a_to_b(self):
        requirement_a = self.requirement_builder.build_for_panel("panel-1", needs_edge_band=True)[0]
        requirement_b = self.requirement_builder.build_for_panel("panel-1", needs_assembly_holes=True)[0]
        operation_a = self.realizer.realize((requirement_a,))[0]
        operation_b = self.realizer.realize((requirement_b,))[0]
        instance_a = self.instantiator.instantiate(operation_a, ("A",), ("geo-a",), ("face-a",))[0]
        instance_b = self.instantiator.instantiate(operation_b, ("B",), ("geo-b",), ("face-b",))[0]
        link = ManufacturingOperationLink(
            link_id=f"{instance_a.operation_instance_item_id}::REQUIRES_PREPARED_GEOMETRY::{instance_b.operation_instance_item_id}",
            predecessor_instance_id=instance_a.operation_instance_item_id,
            successor_instance_id=instance_b.operation_instance_item_id,
            relationship_type="REQUIRES_PREPARED_GEOMETRY",
            reason="A must be prepared before B.",
        )
        graph = self.graph_builder.build((instance_a, instance_b), (link,))
        return graph, instance_a, instance_b

    def test_build_logical_plan_from_graph_with_a_to_b(self):
        graph, instance_a, instance_b = self._build_graph_a_to_b()
        plan = self.plan_builder.build(graph)
        self.assertTrue(is_dataclass(plan))
        self.assertEqual(plan.graph_instance_ids, graph.instance_ids)
        validate_logical_execution_plan_contract(plan)

    def test_a_is_root(self):
        graph, instance_a, instance_b = self._build_graph_a_to_b()
        plan = self.plan_builder.build(graph)
        self.assertIn(instance_a.operation_instance_item_id, plan.root_instance_ids)

    def test_b_is_blocked(self):
        graph, instance_a, instance_b = self._build_graph_a_to_b()
        plan = self.plan_builder.build(graph)
        self.assertIn(instance_b.operation_instance_item_id, plan.blocked_instance_ids)

    def test_b_is_terminal(self):
        graph, instance_a, instance_b = self._build_graph_a_to_b()
        plan = self.plan_builder.build(graph)
        self.assertIn(instance_b.operation_instance_item_id, plan.terminal_instance_ids)

    def test_plan_id_is_deterministic(self):
        graph, instance_a, instance_b = self._build_graph_a_to_b()
        plan = self.plan_builder.build(graph)
        self.assertEqual(
            plan.plan_id,
            "logical-plan::" + "::".join(graph.instance_ids),
        )

    def test_plan_preserves_graph_reference(self):
        graph, instance_a, instance_b = self._build_graph_a_to_b()
        plan = self.plan_builder.build(graph)
        self.assertIs(plan.graph, graph)

    def test_plan_does_not_mutate_graph(self):
        graph, instance_a, instance_b = self._build_graph_a_to_b()
        original_instance_ids = graph.instance_ids
        original_links = graph.links
        original_adjacency = graph.adjacency.copy()
        original_reverse = graph.reverse_adjacency.copy()
        self.plan_builder.build(graph)
        self.assertEqual(graph.instance_ids, original_instance_ids)
        self.assertEqual(graph.links, original_links)
        self.assertEqual(graph.adjacency, original_adjacency)
        self.assertEqual(graph.reverse_adjacency, original_reverse)

    def test_plan_does_not_create_execution_order_or_runtime_fields(self):
        field_names = {field.name for field in fields(ManufacturingLogicalExecutionPlan)}
        for forbidden in (
            "execution_order",
            "priority",
            "batch_id",
            "job_id",
            "queue_id",
            "machine_id",
            "runtime_status",
        ):
            self.assertNotIn(forbidden, field_names)

    def test_metadata_rejects_forbidden_runtime_execution_keys(self):
        graph, instance_a, instance_b = self._build_graph_a_to_b()
        plan = ManufacturingLogicalExecutionPlan(
            plan_id="logical-plan::a::b",
            graph_instance_ids=graph.instance_ids,
            root_instance_ids=(instance_a.operation_instance_item_id,),
            blocked_instance_ids=(instance_b.operation_instance_item_id,),
            terminal_instance_ids=(instance_b.operation_instance_item_id,),
            graph=graph,
            metadata={"batch_id": "batch-1"},
        )
        with self.assertRaises(ValueError):
            validate_logical_execution_plan_contract(plan)

    def test_no_freecad_import(self):
        source = inspect.getsource(operation_execution_plan_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_manufacturing_production_package_import(self):
        source = inspect.getsource(operation_execution_plan_module)
        self.assertNotIn("ManufacturingProductionPackage", source)
        self.assertNotIn("ProductionPackage", source)

    def test_no_cnc_cost_scheduling_operator_terms_in_implementation(self):
        source = inspect.getsource(operation_execution_plan_module).lower()
        for term in ("cnc", "cost", "scheduling", "operator"):
            self.assertNotIn(term, source)


if __name__ == "__main__":
    unittest.main()
