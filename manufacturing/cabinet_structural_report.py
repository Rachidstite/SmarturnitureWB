from dataclasses import dataclass, field

from manufacturing.shelf_structural_report import ShelfStructuralReport


@dataclass
class CabinetStructuralReport:
    structural_risk: str = "LOW"
    stability_risk: str = "LOW"
    requires_center_support: bool = False
    requires_reinforcement: bool = False
    anti_racking_risk: str = "LOW"
    structural_recommendation: str = ""
    shelf_structural: ShelfStructuralReport = field(
        default_factory=ShelfStructuralReport
    )
