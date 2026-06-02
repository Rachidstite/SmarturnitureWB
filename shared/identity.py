from dataclasses import dataclass
from enum import Enum, auto
import re

class SemanticRole(Enum):
    LEFT_SIDE = auto(); RIGHT_SIDE = auto(); TOP = auto(); BOTTOM = auto()
    BACK = auto(); SHELF = auto(); DIVIDER = auto(); PLINTH = auto()
    DOOR = auto(); DRAWER_FACE = auto(); DRAWER_BOX_SIDE = auto()
    DRAWER_BOX_BACK = auto(); DRAWER_BOX_BOTTOM = auto(); GLASS = auto()

def normalize_identity_part(value) -> str:
    text = str(value or "").strip().upper()
    text = re.sub(r"[^A-Z0-9_-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-_")
    return text or "UNSPECIFIED"

@dataclass(frozen=True)
class PanelIdentity:
    cabinet_id: str        # "CAB-001"
    section_id: str        # "SEC-1", "SEC-LEFT", "STRUCTURE"
    role: SemanticRole
    index: int = 0

    @property
    def key(self):
        # استبدال / بـ _ لتجنب مشاكل FreeCAD
        cabinet = normalize_identity_part(self.cabinet_id)
        section = normalize_identity_part(self.section_id)
        role = self.role.name if hasattr(self.role, "name") else normalize_identity_part(self.role)
        return f"{cabinet}_{section}_{role}-{self.index}"

    @classmethod
    def make_shelf(cls, cabinet, sec_idx, shelf_idx):
        return cls(cabinet, f"SEC-{sec_idx+1}", SemanticRole.SHELF, shelf_idx+1)

    @classmethod
    def make_drawer_face(cls, cabinet, sec_idx, drawer_idx):
        return cls(cabinet, f"SEC-{sec_idx+1}", SemanticRole.DRAWER_FACE, drawer_idx+1)

    @classmethod
    def make_door(cls, cabinet, sec_idx, door_idx):
        return cls(cabinet, f"SEC-{sec_idx+1}", SemanticRole.DOOR, door_idx+1)

    @classmethod
    def make_divider(cls, cabinet, sec_idx):
        return cls(cabinet, "STRUCTURE", SemanticRole.DIVIDER, sec_idx+1)

    @classmethod
    def make_side(cls, cabinet, side):
        role = SemanticRole.LEFT_SIDE if side.upper() == "LEFT" else SemanticRole.RIGHT_SIDE
        return cls(cabinet, f"SEC-{side}", role)
