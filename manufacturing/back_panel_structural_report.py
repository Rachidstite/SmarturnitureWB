from dataclasses import dataclass


@dataclass
class BackPanelStructuralReport:
    structural_risk: str = "LOW"
    racking_resistance: str = "UNKNOWN"
    requires_center_support: bool = False
    requires_reinforcement: bool = False
    structural_recommendation: str = ""
