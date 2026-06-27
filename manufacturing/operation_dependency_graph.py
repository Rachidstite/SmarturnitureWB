from __future__ import annotations

from dataclasses import dataclass, field

from manufacturing.operation_instance import (
    ManufacturingOperationInstance,
    validate_operation_instance_contract,
)
from manufacturing.operation_link import (
    FORBIDDEN_LINK_METADATA_KEYS,
    ManufacturingOperationLink,
    validate_operation_link_contract,
)


FORBIDDEN_GRAPH_METADATA_KEYS = FORBIDDEN_LINK_METADATA_KEYS | {
    "start_time",
    "end_time",
    "priority",
    "assigned_to",
}


@dataclass(frozen=True)
class ManufacturingOperationDependencyGraph:
    instance_ids: tuple[str, ...]
    links: tuple[ManufacturingOperationLink, ...]
    adjacency: dict[str, tuple[str, ...]]
    reverse_adjacency: dict[str, tuple[str, ...]]
    metadata: dict = field(default_factory=dict)


def validate_operation_dependency_graph_contract(
    graph: ManufacturingOperationDependencyGraph,
) -> None:
    if not isinstance(graph.instance_ids, tuple):
        raise TypeError("instance_ids must be a tuple")
    if not isinstance(graph.links, tuple):
        raise TypeError("links must be a tuple")
    if not isinstance(graph.adjacency, dict):
        raise TypeError("adjacency must be a dict")
    if not isinstance(graph.reverse_adjacency, dict):
        raise TypeError("reverse_adjacency must be a dict")
    if not isinstance(graph.metadata, dict):
        raise TypeError("metadata must be a dict")
    instance_ids = set(graph.instance_ids)
    for link in graph.links:
        validate_operation_link_contract(link)
        if link.predecessor_instance_id not in instance_ids:
            raise ValueError("link predecessor must exist in instance_ids")
        if link.successor_instance_id not in instance_ids:
            raise ValueError("link successor must exist in instance_ids")
    forbidden_keys = FORBIDDEN_GRAPH_METADATA_KEYS.intersection(graph.metadata.keys())
    if forbidden_keys:
        raise ValueError(f"metadata contains forbidden keys: {sorted(forbidden_keys)}")


class ManufacturingOperationDependencyGraphBuilder:
    def build(
        self,
        instances: tuple[ManufacturingOperationInstance, ...],
        links: tuple[ManufacturingOperationLink, ...],
    ) -> ManufacturingOperationDependencyGraph:
        instance_ids = []
        for instance in instances:
            validate_operation_instance_contract(instance)
            instance_ids.append(instance.operation_instance_item_id)

        instance_id_set = set(instance_ids)
        adjacency_lists: dict[str, list[str]] = {}
        reverse_lists: dict[str, list[str]] = {}

        for link in links:
            validate_operation_link_contract(link)
            if link.predecessor_instance_id not in instance_id_set:
                raise ValueError("link predecessor must exist in instance_ids")
            if link.successor_instance_id not in instance_id_set:
                raise ValueError("link successor must exist in instance_ids")
            adjacency_lists.setdefault(link.predecessor_instance_id, []).append(
                link.successor_instance_id
            )
            reverse_lists.setdefault(link.successor_instance_id, []).append(
                link.predecessor_instance_id
            )

        adjacency = {
            instance_id: tuple(adjacency_lists.get(instance_id, ()))
            for instance_id in instance_ids
        }
        reverse_adjacency = {
            instance_id: tuple(reverse_lists.get(instance_id, ()))
            for instance_id in instance_ids
        }

        graph = ManufacturingOperationDependencyGraph(
            instance_ids=tuple(instance_ids),
            links=links,
            adjacency=adjacency,
            reverse_adjacency=reverse_adjacency,
            metadata={},
        )
        validate_operation_dependency_graph_contract(graph)
        return graph
