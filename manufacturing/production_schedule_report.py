from dataclasses import dataclass, field


@dataclass
class ProductionScheduleReport:
    required_work_days: float = 0.0
    required_machine_days: float = 0.0
    required_operator_days: float = 0.0
    capacity_utilization_percent: float = 0.0
    schedule_risk_level: str = "LOW"
    warnings: list = field(default_factory=list)
