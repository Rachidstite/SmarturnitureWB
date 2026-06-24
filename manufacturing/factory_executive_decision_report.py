from dataclasses import dataclass


@dataclass
class FactoryExecutiveDecisionReport:
    business_status: str = "APPROVED"
    profitability_status: str = "HEALTHY"
    delivery_status: str = "ON_TRACK"
    executive_recommendation: str = ""
