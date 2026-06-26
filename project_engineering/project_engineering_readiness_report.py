from dataclasses import dataclass


@dataclass
class ProjectEngineeringReadinessReport:
    project_id: str = ""
    ready_for_engineering_release: bool = False
    ready_for_manufacturing_handoff: bool = False
    blocking_violation_count: int = 0
    warning_count: int = 0
    source: str = ""
