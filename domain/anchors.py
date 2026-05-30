from dataclasses import dataclass
from enum import Enum

class MountFace(str, Enum):
    """الوجه المادي للوح الذي سيتم التثبيت أو التخريم عليه"""
    FRONT = "FRONT"
    BACK = "BACK"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    TOP = "TOP"
    BOTTOM = "BOTTOM"

class EdgeRef(str, Enum):
    """الحافة المرجعية التي سيتم القياس منها (أساس الـ Associative CAD)"""
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    FRONT = "FRONT"   # ⚡ تمت الإضافة: الحافة الأمامية
    BACK = "BACK"     # ⚡ تمت الإضافة: الحافة الخلفية
    CENTER = "CENTER"

@dataclass
class AnchorCoordinate:
    """إحداثيات دلالية: القياس بالنسبة لحافة معينة على وجه معين"""
    face: MountFace
    edge: EdgeRef
    offset_x: float
    offset_y: float

    def to_dict(self) -> dict:
        return {
            "face": self.face.value if hasattr(self.face, 'value') else self.face,
            "edge": self.edge.value if hasattr(self.edge, 'value') else self.edge,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y
        }

@dataclass
class HardwarePlacement:
    """رابط دلالي يحدد نية التثبيت (Intent) قبل تحويلها لعمليات CNC"""
    host_node_id: str
    hardware_intent: str       # النية (مثل: INTENT_HINGE)
    anchor: AnchorCoordinate
    target_node_id: str = ""   # اللوح المقابل (إن وُجد)
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "host_node_id": self.host_node_id,
            "target_node_id": self.target_node_id,
            "hardware_intent": self.hardware_intent,
            "anchor": self.anchor.to_dict(),
            "description": self.description
        }
