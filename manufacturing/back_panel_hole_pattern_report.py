from dataclasses import dataclass


@dataclass
class BackPanelHolePatternReport:
    horizontal_hole_count: int = 0
    vertical_hole_count: int = 0
    total_hole_count: int = 0
    top_edge_holes: int = 0
    bottom_edge_holes: int = 0
    left_edge_holes: int = 0
    right_edge_holes: int = 0
    pattern_type: str = ""
    center_hole_count: int = 0
