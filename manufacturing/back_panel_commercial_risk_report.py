from dataclasses import dataclass


@dataclass
class BackPanelCommercialRiskReport:
    risk_level: str = ""
    rework_risk: str = ""
    scrap_risk: str = ""
    labor_delay_risk: str = ""
    cnc_error_risk: str = ""
    customer_complaint_risk: str = ""
    profitability_impact: str = ""
    estimated_waste_category: str = ""
    commercial_warning: str = ""
    recommended_commercial_action: str = ""
