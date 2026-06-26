from project_engineering.project_adjacency_fact import ProjectAdjacencyFact
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)


def build_project_adjacency_fact(
    first: SceneNodeBoundsMeasurement,
    second: SceneNodeBoundsMeasurement,
    tolerance_mm: float = 0.0,
) -> ProjectAdjacencyFact:
    def overlaps_or_touches(a_min: float, a_max: float, b_min: float, b_max: float) -> bool:
        return max(a_min, b_min) <= min(a_max, b_max)

    x_gap_forward = second.x_min - first.x_max
    x_gap_backward = first.x_min - second.x_max
    y_gap_forward = second.y_min - first.y_max
    y_gap_backward = first.y_min - second.y_max

    if (
        abs(x_gap_forward) <= tolerance_mm
        and overlaps_or_touches(first.y_min, first.y_max, second.y_min, second.y_max)
    ):
        return ProjectAdjacencyFact(
            first_component_id=first.node_id,
            second_component_id=second.node_id,
            relation="adjacent",
            axis="x",
            distance_mm=x_gap_forward,
            source="project-adjacency-builder",
        )

    if (
        abs(x_gap_backward) <= tolerance_mm
        and overlaps_or_touches(first.y_min, first.y_max, second.y_min, second.y_max)
    ):
        return ProjectAdjacencyFact(
            first_component_id=first.node_id,
            second_component_id=second.node_id,
            relation="adjacent",
            axis="x",
            distance_mm=x_gap_backward,
            source="project-adjacency-builder",
        )

    if (
        abs(y_gap_forward) <= tolerance_mm
        and overlaps_or_touches(first.x_min, first.x_max, second.x_min, second.x_max)
    ):
        return ProjectAdjacencyFact(
            first_component_id=first.node_id,
            second_component_id=second.node_id,
            relation="adjacent",
            axis="y",
            distance_mm=y_gap_forward,
            source="project-adjacency-builder",
        )

    if (
        abs(y_gap_backward) <= tolerance_mm
        and overlaps_or_touches(first.x_min, first.x_max, second.x_min, second.x_max)
    ):
        return ProjectAdjacencyFact(
            first_component_id=first.node_id,
            second_component_id=second.node_id,
            relation="adjacent",
            axis="y",
            distance_mm=y_gap_backward,
            source="project-adjacency-builder",
        )

    x_separation = max(x_gap_forward, x_gap_backward, 0.0)
    y_separation = max(y_gap_forward, y_gap_backward, 0.0)
    if x_separation > 0.0 and y_separation > 0.0:
        distance_mm = min(x_separation, y_separation)
    else:
        distance_mm = x_separation or y_separation or 0.0

    return ProjectAdjacencyFact(
        first_component_id=first.node_id,
        second_component_id=second.node_id,
        relation="separate",
        axis="",
        distance_mm=distance_mm,
        source="project-adjacency-builder",
    )
