from dataclasses import dataclass


@dataclass
class FactoryCapacitySimulationReport:
    required_factory_minutes: float = 0.0
    available_factory_minutes: float = 0.0
    capacity_usage_percent: float = 0.0
    capacity_status: str = "AVAILABLE"
    capacity_recommendation: str = ""
