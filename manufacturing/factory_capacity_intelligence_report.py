from dataclasses import dataclass


@dataclass
class FactoryCapacityIntelligenceReport:
    required_hours: float = 0.0
    weekly_capacity_hours: float = 0.0
    utilization_percent: float = 0.0
    remaining_capacity_hours: float = 0.0
    status: str = "UNKNOWN"
