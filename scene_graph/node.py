from dataclasses import dataclass, field
from typing import List, Dict, Any
from shared.identity import PanelIdentity
from shared.roles import NodeRole
from manufacturing.edge_spec import EdgeSpec

@dataclass
class SceneNode:
    identity: PanelIdentity
    width: float
    depth: float
    height: float
    x: float
    y: float
    z: float
    thickness: float = 0.0  # السماكة التصنيعية الصريحة
    material: str = "MDF_18MM"
    edge_bandings: str = ""
    group: str = "Carcass"
    edge_spec: EdgeSpec = None  # ✅ نظام الحواف           # تنظيم المجموعات
    role: NodeRole = NodeRole.SHELF  # افتراضي                   # DRAWER_FACE, DOOR, SHELF, ...
    metadata: Dict[str, Any] = field(default_factory=dict)  # بيانات تصنيع إضافية
