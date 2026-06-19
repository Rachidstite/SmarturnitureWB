from dataclasses import dataclass


@dataclass
class FactoryGovernancePolicyContext:
    readiness_status: str = ""
    profitability_status: str = ""
    capacity_status: str = ""
    load_status: str = ""
    schedule_status: str = ""
    risk_status: str = ""
    executive_status: str = ""
