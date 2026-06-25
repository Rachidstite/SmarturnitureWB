from dataclasses import dataclass, field


@dataclass
class ProjectOperationalReadinessReport:
    project_id: str
    ready_for_operation: bool = True
    ready_for_installation: bool = True
    ready_for_service: bool = True
    overall_ready: bool = True
    cabinet_count: int = 0
    ready_cabinet_count: int = 0
    warning_cabinet_count: int = 0
    violation_cabinet_count: int = 0
    warnings: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    source: str = ""
