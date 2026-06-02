from dataclasses import dataclass

@dataclass
class DoorMetadata:
    door_type: str
    layer: int = 0
    cnc_enabled: bool = False

@dataclass
class DrawerMetadata:
    drawer_type: str
    box_w: float; box_h: float; box_d: float
    box_x: float; box_y: float; box_z: float
    bottom_thickness: float

@dataclass
class BackPanelMetadata:
    section_index: int
    section_label: str
    is_section_back: bool
    groove_depth: float
    back_offset: float
    extends_into_groove: bool
    source_rule: str
