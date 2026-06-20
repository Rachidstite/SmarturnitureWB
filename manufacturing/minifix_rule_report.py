from dataclasses import dataclass


@dataclass
class MinifixRuleReport:
    minimum_edge_distance: float = 0.0
    minimum_panel_thickness: float = 0.0
    minimum_spacing: float = 0.0
    maximum_spacing: float = 0.0
    requires_cam_lock: bool = False
    requires_dowel_support: bool = False
    recommended_pattern: str = ""
    recommended_quantity: int = 0
