from dataclasses import dataclass


@dataclass
class ProductionForecastReport:
    required_factory_minutes: float = 0.0
    available_factory_minutes_per_day: float = 0.0
    estimated_production_days: float = 0.0
    forecast_status: str = "ON_SCHEDULE"
    forecast_recommendation: str = ""
