from dataclasses import dataclass


@dataclass
class BackPanelHoleRuleReport:
    minimum_panel_width: float = 0.0
    minimum_panel_height: float = 0.0

    spacing_rule: str = ""
    edge_rule: str = ""
    corner_rule: str = ""

    maximum_spacing: float = 0.0

    requires_center_holes: bool = False
