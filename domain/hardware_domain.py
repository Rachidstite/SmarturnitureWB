from dataclasses import dataclass, field
from domain.core_types import NodeCategory, NodeRole
from domain.topology import Transform3D
from typing import List

@dataclass
class MachiningOperation:
    """وحدة التعليمات لآلات الـ CNC (تخريم، تفريز)"""
    op_type: str  # "DRILL", "ROUTING"
    diameter: float
    depth: float
    transform: Transform3D # إحداثيات العملية بالنسبة للقطعة الأم

@dataclass
class HardwareNode:
    """كيان الإكسسوارات (مفصلة، مينيفكس، برغي)"""
    identity: any
    role: NodeRole
    category: NodeCategory = NodeCategory.HARDWARE
    transform: Transform3D = field(default_factory=Transform3D)
    operations: List[MachiningOperation] = field(default_factory=list)

    def to_dict(self):
        return {
            "identity": {"key": self.identity.key},
            "role": self.role.value,
            "category": self.category.value,
            "transform": self.transform.__dict__,
            "ops": [op.__dict__ for op in self.operations]
        }
