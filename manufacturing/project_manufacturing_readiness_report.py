from dataclasses import dataclass


@dataclass
class ProjectManufacturingReadinessReport:
    readiness_status: str = "READY"
    structural_risk: str = "LOW"
    engineering_review_required: bool = False
    manufacturing_recommendation: str = ""
