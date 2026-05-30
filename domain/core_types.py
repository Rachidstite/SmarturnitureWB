from enum import Enum
from dataclasses import dataclass

class NodeCategory(str, Enum):
    PHYSICAL = "PHYSICAL"
    VIRTUAL = "VIRTUAL"
    HARDWARE = "HARDWARE"
    REFERENCE = "REFERENCE"

class NodeRole(str, Enum):
    SIDE_PANEL = "SIDE_PANEL"
    TOP_PANEL = "TOP_PANEL"
    BOTTOM_PANEL = "BOTTOM_PANEL"
    BACK_PANEL = "BACK_PANEL"
    DIVIDER = "DIVIDER"
    SHELF = "SHELF"
    DOOR_PANEL = "DOOR_PANEL"
    DRAWER_FRONT = "DRAWER_FRONT"
    VIRTUAL_ANCHOR = "VIRTUAL_ANCHOR"
    UNKNOWN = "UNKNOWN"

class JoineryType(str, Enum):
    MINIFIX_15 = "MINIFIX_15"
    CONFIRMAT_50 = "CONFIRMAT_50"
    SHELF_PIN_5MM = "SHELF_PIN_5MM"
    HINGE_HALF_OVERLAY = "HINGE_HALF_OVERLAY"
    VIRTUAL_LINK = "VIRTUAL_LINK"

@dataclass
class MachiningOperation:
    op_type: str
    diameter: float
    depth: float
    face: str
    local_x: float
    local_y: float
    axis: str = "Z" # ⚡ Ensure Axis is always present for Save/Load
    is_through: bool = False

    def to_dict(self):
        return self.__dict__
