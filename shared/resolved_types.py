from dataclasses import dataclass
from .enums import DoorType
@dataclass(frozen=True)
class ResolvedShelf: x: float; y: float; z: float; width: float; depth: float
@dataclass(frozen=True)
class ResolvedDrawer: face_x: float; face_y: float; face_z: float; face_w: float; face_h: float; box_x: float; box_y: float; box_z: float; box_w: float; box_h: float; box_d: float; bottom_thickness: float
@dataclass(frozen=True)
class ResolvedDoor: x: float; y: float; z: float; width: float; height: float; door_type: DoorType; layer: int = 0
@dataclass(frozen=True)
class ResolvedDivider: x: float; y: float; z: float; width: float; depth: float; height: float
@dataclass(frozen=True)
class ResolvedTopPanel: width: float; depth: float; thickness: float; x: float; y: float; z: float
@dataclass(frozen=True)
class ResolvedSection:
    inner_x: float; inner_width: float; shelf_width: float; drawer_box_width: float
    left_overlay: float; right_overlay: float; door_x: float; door_width: float
    drawer_face_x: float; drawer_face_width: float; divider_x: float; has_sliding_system: bool
    shelves: tuple = (); drawers: tuple = (); doors: tuple = (); divider: ResolvedDivider = None
