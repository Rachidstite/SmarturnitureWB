from dataclasses import dataclass


@dataclass
class ConfirmatPlacementReport:
    host_panel_id: str = ""
    target_panel_id: str = ""
    x_position: float = 0.0
    y_position: float = 0.0
    z_position: float = 0.0
    face: str = ""
    axis: str = ""
    placement_type: str = ""
