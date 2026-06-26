from project_engineering.project_adjacency_fact import ProjectAdjacencyFact
from project_engineering.project_alignment_fact import ProjectAlignmentFact
from project_engineering.project_collision_fact import ProjectCollisionFact
from project_engineering.project_envelope import ProjectEnvelope
from project_engineering.project_footprint import ProjectFootprint
from project_engineering.project_spatial_summary_report import (
    ProjectSpatialSummaryReport,
)


def build_project_spatial_summary_report(
    project_id: str,
    envelope: ProjectEnvelope,
    footprint: ProjectFootprint,
    adjacency_facts: list[ProjectAdjacencyFact],
    alignment_facts: list[ProjectAlignmentFact],
    collision_facts: list[ProjectCollisionFact],
) -> ProjectSpatialSummaryReport:
    collision_count = len(collision_facts)

    return ProjectSpatialSummaryReport(
        project_id=project_id,
        envelope_source=envelope.source,
        footprint_source=footprint.source,
        adjacency_count=len(adjacency_facts),
        alignment_count=len(alignment_facts),
        collision_count=collision_count,
        has_collisions=collision_count > 0,
        source="project-spatial-summary-builder",
    )
