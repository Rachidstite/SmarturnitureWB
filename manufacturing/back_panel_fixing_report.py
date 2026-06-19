from dataclasses import dataclass

from manufacturing.back_panel_fixing_strategy import BackPanelFixingStrategy


@dataclass
class BackPanelFixingReport:
    strategy: BackPanelFixingStrategy = BackPanelFixingStrategy.GROOVE
    requires_holes: bool = False
    requires_groove: bool = True
    requires_fasteners: bool = False
    structural_rating: float = 0.0
    manufacturing_notes: str = ""
