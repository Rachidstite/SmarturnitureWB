from dataclasses import dataclass


@dataclass
class DrawerSlidePlacementReport:
    drawer_id: str = ""
    slide_side: str = ""
    cabinet_panel_id: str = ""
    drawer_panel_id: str = ""
    x_position: float = 0.0
    y_position: float = 0.0
    z_position: float = 0.0
    mounting_face: str = ""
    placement_type: str = ""
