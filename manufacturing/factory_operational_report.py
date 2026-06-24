from dataclasses import dataclass


@dataclass
class FactoryOperationalReport:
    operational_status: str = "READY"
    delivery_risk: str = "LOW"
    capacity_risk: str = "LOW"
    management_recommendation: str = ""
