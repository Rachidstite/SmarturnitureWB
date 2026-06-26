from project_engineering.project_adjacency_builder import build_project_adjacency_fact
from project_engineering.project_adjacency_fact import ProjectAdjacencyFact
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)


def aggregate_project_adjacency_facts(
    bounds_measurements: list[SceneNodeBoundsMeasurement],
    tolerance_mm: float = 0.0,
) -> list[ProjectAdjacencyFact]:
    facts: list[ProjectAdjacencyFact] = []

    for index, first in enumerate(bounds_measurements):
        for second in bounds_measurements[index + 1 :]:
            facts.append(
                build_project_adjacency_fact(first, second, tolerance_mm=tolerance_mm)
            )

    return facts
