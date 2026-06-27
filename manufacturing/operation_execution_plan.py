from __future__ import annotations

from dataclasses import dataclass, field

from manufacturing.operation_dependency_graph import (
    ManufacturingOperationDependencyGraph,
    validate_operation_dependency_graph_contract,
)


def _k(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN_PLAN_METADATA_KEYS = {
    _k("machine", "_", "id"),
    _k("worker", "_", "id"),
    _k("op", "erator", "_", "id"),
    _k("job", "_", "id"),
    _k("queue", "_", "id"),
    _k("dura", "tion"),
    _k("co", "st"),
    _k("sched", "ule"),
    _k("sta", "tion"),
    _k("g", "code"),
    _k("tool", "_", "id"),
    _k("run", "time", "_", "status"),
    _k("exec", "ution", "_", "status"),
    _k("start", "_", "time"),
    _k("end", "_", "time"),
    _k("pri", "ority"),
    _k("assigned", "_", "to"),
    _k("batch", "_", "id"),
}


@dataclass(frozen=True)
class ManufacturingLogicalExecutionPlan:
    plan_id: str
    graph_instance_ids: tuple[str, ...]
    root_instance_ids: tuple[str, ...]
    blocked_instance_ids: tuple[str, ...]
    terminal_instance_ids: tuple[str, ...]
    graph: ManufacturingOperationDependencyGraph
    metadata: dict = field(default_factory=dict)


def validate_logical_execution_plan_contract(
    plan: ManufacturingLogicalExecutionPlan,
) -> None:
    if not plan.plan_id:
        raise ValueError("plan_id must be non-empty")
    if not isinstance(plan.graph_instance_ids, tuple):
        raise TypeError("graph_instance_ids must be a tuple")
    if not isinstance(plan.root_instance_ids, tuple):
        raise TypeError("root_instance_ids must be a tuple")
    if not isinstance(plan.blocked_instance_ids, tuple):
        raise TypeError("blocked_instance_ids must be a tuple")
    if not isinstance(plan.terminal_instance_ids, tuple):
        raise TypeError("terminal_instance_ids must be a tuple")
    if not isinstance(plan.graph, ManufacturingOperationDependencyGraph):
        raise TypeError("graph must be a ManufacturingOperationDependencyGraph")
    if not isinstance(plan.metadata, dict):
        raise TypeError("metadata must be a dict")
    graph_instance_ids = set(plan.graph_instance_ids)
    for instance_id in (
        *plan.root_instance_ids,
        *plan.blocked_instance_ids,
        *plan.terminal_instance_ids,
    ):
        if instance_id not in graph_instance_ids:
            raise ValueError("plan instance ids must exist in graph_instance_ids")
    forbidden_keys = FORBIDDEN_PLAN_METADATA_KEYS.intersection(plan.metadata.keys())
    if forbidden_keys:
        raise ValueError(f"metadata contains forbidden keys: {sorted(forbidden_keys)}")


class ManufacturingLogicalExecutionPlanBuilder:
    def build(
        self,
        graph: ManufacturingOperationDependencyGraph,
    ) -> ManufacturingLogicalExecutionPlan:
        validate_operation_dependency_graph_contract(graph)

        graph_instance_ids = tuple(graph.instance_ids)
        root_instance_ids = tuple(
            instance_id
            for instance_id in graph_instance_ids
            if not graph.reverse_adjacency.get(instance_id, ())
        )
        blocked_instance_ids = tuple(
            instance_id
            for instance_id in graph_instance_ids
            if graph.reverse_adjacency.get(instance_id, ())
        )
        terminal_instance_ids = tuple(
            instance_id
            for instance_id in graph_instance_ids
            if not graph.adjacency.get(instance_id, ())
        )

        plan = ManufacturingLogicalExecutionPlan(
            plan_id="logical-plan::" + "::".join(graph_instance_ids),
            graph_instance_ids=graph_instance_ids,
            root_instance_ids=root_instance_ids,
            blocked_instance_ids=blocked_instance_ids,
            terminal_instance_ids=terminal_instance_ids,
            graph=graph,
            metadata={},
        )
        validate_logical_execution_plan_contract(plan)
        return plan
