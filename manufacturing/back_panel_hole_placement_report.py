from dataclasses import dataclass, field


@dataclass
class BackPanelHoleCoordinate:
    x: float = 0.0
    y: float = 0.0
    diameter: float = 0.0
    depth: float = 0.0
    face: str = ""


@dataclass
class BackPanelHolePlacementReport:
    edge_distance: float = 0.0
    corner_offset: float = 0.0
    minimum_hole_count: int = 0
    maximum_hole_count: int = 0
    default_spacing: float = 0.0
    supports_screws: bool = False
    supports_confirmat: bool = False
    hole_positions: list = field(default_factory=list)
