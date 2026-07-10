from __future__ import annotations

from types import SimpleNamespace

from domain.base_cabinet_engineering_entry import (
    build_base_cabinet_engineering_cabinet,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import BaseCabinetSpecificationAdapter
from domain.constraint_engine import CabinetConstraintValidator
from domain.diagnostics import ValidationReport


def _graph_with_physical_nodes(scene_graph):
    if scene_graph is None:
        return SimpleNamespace(
            physical_nodes=[],
            nodes=[],
            _by_role={},
            _by_category={},
        )

    physical_nodes = getattr(scene_graph, "physical_nodes", None)
    if physical_nodes is None:
        if hasattr(scene_graph, "all_nodes"):
            physical_nodes = list(scene_graph.all_nodes())
        else:
            physical_nodes = list(getattr(scene_graph, "nodes", []) or [])
    else:
        physical_nodes = list(physical_nodes or [])

    nodes = getattr(scene_graph, "nodes", None)
    if nodes is None:
        nodes = physical_nodes
    else:
        nodes = list(nodes or [])

    normalized_nodes = [_validation_node(node) for node in physical_nodes]

    return SimpleNamespace(
        physical_nodes=normalized_nodes,
        nodes=normalized_nodes if nodes is physical_nodes else [_validation_node(node) for node in nodes],
        _by_role=getattr(scene_graph, "_by_role", {}),
        _by_category=getattr(scene_graph, "_by_category", {}),
    )


def _validation_node(node):
    node_data = dict(vars(node))
    role = node_data.get("role", None)
    node_data["role"] = getattr(role, "name", role)
    return SimpleNamespace(**node_data)


def _validation_project_from_cabinet(cabinet, adapter_result):
    cabinet_params = getattr(cabinet, "params", adapter_result.cabinet_params)
    scene_graph = getattr(cabinet, "graph", None) or getattr(
        cabinet,
        "scene_graph",
        None,
    )
    joinery = getattr(cabinet, "joinery", None)
    if joinery is None:
        joinery = SimpleNamespace(edges=[])
    elif not hasattr(joinery, "edges"):
        joinery = SimpleNamespace(edges=[])

    topology = SimpleNamespace(
        sections={
            0: SimpleNamespace(
                width=cabinet_params.width,
                height=cabinet_params.height,
                depth=cabinet_params.depth,
            )
        }
    )

    return SimpleNamespace(
        params=cabinet_params,
        topology=topology,
        graph=_graph_with_physical_nodes(scene_graph),
        joinery=joinery,
        metadata=dict(adapter_result.metadata),
    )


def validate_base_cabinet_specification(
    specification: BaseCabinetSpecification,
    cabinet=None,
) -> ValidationReport:
    adapter_result = BaseCabinetSpecificationAdapter.adapt(specification)
    validation_cabinet = cabinet
    if validation_cabinet is None:
        validation_cabinet = build_base_cabinet_engineering_cabinet(specification)
    project = _validation_project_from_cabinet(
        validation_cabinet,
        adapter_result,
    )
    return CabinetConstraintValidator(project).validate_all()
