from dataclasses import dataclass


@dataclass
class DrawerStructuralReport:
    structural_risk: str = "LOW"
    slide_capacity_risk: str = "LOW"
    bottom_panel_risk: str = "LOW"
    requires_reinforcement: bool = False
    structural_recommendation: str = ""
