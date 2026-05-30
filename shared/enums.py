from enum import Enum, auto
class DoorType(Enum):
    NONE = 0; INSET = auto(); OVERLAY = auto(); SLIDING = auto()
    GLASS_INSET = auto(); GLASS_OVERLAY = auto(); GLASS_SLIDING = auto()
    @classmethod
    def from_string(cls, s: str):
        mapping = {"None": cls.NONE, "Inset": cls.INSET, "Overlay": cls.OVERLAY, "Sliding": cls.SLIDING,
                   "Glass Inset": cls.GLASS_INSET, "Glass Overlay": cls.GLASS_OVERLAY, "Glass Sliding": cls.GLASS_SLIDING}
        return mapping.get(s, cls.NONE)
    def is_glass(self): return self in (DoorType.GLASS_INSET, DoorType.GLASS_OVERLAY, DoorType.GLASS_SLIDING)
    def is_overlay(self): return self in (DoorType.OVERLAY, DoorType.GLASS_OVERLAY)
    def is_sliding(self): return self in (DoorType.SLIDING, DoorType.GLASS_SLIDING)
    def is_inset(self): return self in (DoorType.INSET, DoorType.GLASS_INSET)
class DrawerLayoutMode(Enum): MANUAL = auto(); EQUAL = auto()
class Domain(Enum): GENERAL = "GENERAL"; GEOMETRY = "GEOMETRY"; HARDWARE = "HARDWARE"; CNC = "CNC"; MANUFACTURING = "MANUFACTURING"; CONSTRAINT = "CONSTRAINT"
