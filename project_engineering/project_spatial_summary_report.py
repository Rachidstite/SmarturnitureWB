from dataclasses import dataclass


@dataclass
class ProjectSpatialSummaryReport:
    project_id: str = ""
    envelope_source: str = ""
    footprint_source: str = ""
    adjacency_count: int = 0
    alignment_count: int = 0
    collision_count: int = 0
    has_collisions: bool = False
    source: str = ""
