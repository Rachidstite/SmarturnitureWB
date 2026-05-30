from enum import Enum, auto

class NodeRole(Enum):
    """الأدوار التصنيعية لكل عقدة في المشهد."""
    SIDE_PANEL = auto()      # LEFT_SIDE, RIGHT_SIDE
    TOP_PANEL = auto()
    BOTTOM_PANEL = auto()
    BACK_PANEL = auto()
    SHELF = auto()
    DIVIDER = auto()
    PLINTH = auto()
    DRAWER_FACE = auto()
    DOOR_PANEL = auto()
    DOOR_GLASS = auto()
    DRAWER_BOX_SIDE = auto()
    DRAWER_BOX_BACK = auto()
    DRAWER_BOX_BOTTOM = auto()
    HINGE = auto()
    MINIFIX = auto()
