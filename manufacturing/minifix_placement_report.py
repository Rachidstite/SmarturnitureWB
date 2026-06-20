from dataclasses import dataclass


@dataclass
class MinifixPlacementReport:
    panel_id: str = ""
    x_position: float = 0.0
    y_position: float = 0.0
    z_position: float = 0.0
    face: str = ""
    cam_position: str = ""
    dowel_position: str = ""
    placement_type: str = ""
