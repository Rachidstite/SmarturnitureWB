from dataclasses import dataclass, field


@dataclass
class ManufacturingCapacityReport:
    total_production_hours: float = 0.0
    daily_capacity_hours: float = 8.0
    estimated_days_required: float = 0.0
    capacity_utilization_percent: float = 0.0
    capacity_status: str = "AVAILABLE"
    warnings: list = field(default_factory=list)
