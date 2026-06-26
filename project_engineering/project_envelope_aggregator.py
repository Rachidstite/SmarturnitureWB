from project_engineering.project_envelope import ProjectEnvelope
from project_engineering.project_envelope_builder import build_project_envelope
from project_engineering.project_envelope_from_bounds_adapter import (
    build_project_envelope_from_bounds,
)
from project_engineering.scene_node_bounds_measurement import (
    SceneNodeBoundsMeasurement,
)


def aggregate_project_envelope_from_bounds(
    bounds_measurements: list[SceneNodeBoundsMeasurement],
) -> ProjectEnvelope:
    envelopes = [
        build_project_envelope_from_bounds(bounds)
        for bounds in bounds_measurements
    ]
    return build_project_envelope(envelopes)
