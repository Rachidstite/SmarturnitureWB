from project_engineering.project_envelope import ProjectEnvelope
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)


def build_project_envelope_from_bounds(
    bounds: SceneNodeBoundsMeasurement,
) -> ProjectEnvelope:
    return ProjectEnvelope(
        x_min=bounds.x_min,
        y_min=bounds.y_min,
        z_min=bounds.z_min,
        x_max=bounds.x_max,
        y_max=bounds.y_max,
        z_max=bounds.z_max,
        source="project-envelope-from-bounds",
    )
