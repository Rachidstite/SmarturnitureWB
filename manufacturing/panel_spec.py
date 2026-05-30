from dataclasses import dataclass, field
from typing import List
from shared.roles import NodeRole
from manufacturing.edge_spec import EdgeSpec

@dataclass
class PanelSpec:
    """مواصفات تصنيعية مجردة – لا تعتمد على محاور XYZ."""
    identity: str
    role: NodeRole
    width: float
    height: float
    thickness: float
    material: str
    grain_direction: str = "NONE"
    edge_spec: EdgeSpec = field(default_factory=EdgeSpec)  # ✅ نظام الحواف الجديد
    quantity: int = 1
    group: str = ""
    cnc_operations: List[str] = field(default_factory=list)
