from dataclasses import dataclass


@dataclass
class BackPanelHolePlacementReport:
    edge_distance: float = 0.0
    corner_offset: float = 0.0
    minimum_hole_count: int = 0
    maximum_hole_count: int = 0
    default_spacing: float = 0.0
    supports_screws: bool = False
    supports_confirmat: bool = False
