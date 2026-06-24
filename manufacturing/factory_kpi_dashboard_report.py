from dataclasses import dataclass


@dataclass
class FactoryKPIDashboardReport:
    factory_status: str = "UNKNOWN"
    capacity_usage_percent: float = 0.0
    forecast_days: float = 0.0
    delivery_status: str = "UNKNOWN"
    main_bottleneck: str = ""
    total_manufacturing_cost: float = 0.0
    hardware_cost: float = 0.0
    waste_cost: float = 0.0
    recovered_value: float = 0.0
    dashboard_recommendation: str = ""
