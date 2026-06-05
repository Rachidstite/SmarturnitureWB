from dataclasses import dataclass, field
from typing import List
from domain.manufacturing_ops import ManufacturingOperation
from shared.roles import NodeRole
from manufacturing.edge_spec import EdgeSpec
from manufacturing.unified_manufacturing_operation import UnifiedManufacturingOperation

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
    cnc_operations: List[ManufacturingOperation] = field(default_factory=list)
    unified_operations: List[UnifiedManufacturingOperation] = field(default_factory=list)

    @property
    def edge_banding(self):
        return self.edge_spec
