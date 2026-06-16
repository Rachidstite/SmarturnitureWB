from dataclasses import dataclass, field


@dataclass
class FactoryWorkloadReport:
    active_project_count: int = 0
    total_required_work_days: float = 0.0
    average_required_work_days: float = 0.0
    highest_schedule_risk_level: str = "LOW"
    factory_workload_status: str = "AVAILABLE"
    warnings: list = field(default_factory=list)
