from project_engineering.project_envelope import ProjectEnvelope
from project_engineering.project_footprint import ProjectFootprint


def build_project_footprint_from_envelope(
    envelope: ProjectEnvelope,
) -> ProjectFootprint:
    return ProjectFootprint(
        x_min=envelope.x_min,
        y_min=envelope.y_min,
        x_max=envelope.x_max,
        y_max=envelope.y_max,
        source="project-footprint-builder",
    )
