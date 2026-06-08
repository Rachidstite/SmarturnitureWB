from dataclasses import dataclass

@dataclass
class DoorMetadata:
    door_type: str
    door_width: float
    door_height: float
    layer: int = 0
    cnc_enabled: bool = False

@dataclass
class DrawerMetadata:
    drawer_type: str
    box_w: float; box_h: float; box_d: float
    box_x: float; box_y: float; box_z: float
    bottom_thickness: float
