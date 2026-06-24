from dataclasses import dataclass


@dataclass
class CabinetStabilityReport:
    tipping_risk: str = "LOW"
    wall_anchoring_required: bool = False
    large_span_risk: str = "LOW"
    stability_recommendation: str = ""
