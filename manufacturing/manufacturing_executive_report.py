from dataclasses import dataclass


@dataclass
class ManufacturingExecutiveReport:
    overall_status: str = "UNKNOWN"
    decision_status: str = "UNKNOWN"
    manufacturing_status: str = "UNKNOWN"
    delivery_status: str = "UNKNOWN"
    production_forecast_status: str = "UNKNOWN"
    primary_factory_risk: str = ""
    recommended_action: str = ""
    executive_summary: str = ""
