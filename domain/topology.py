from dataclasses import dataclass, field
from typing import Dict, Tuple

@dataclass
class Transform3D:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rot_x: float = 0.0
    rot_y: float = 0.0
    rot_z: float = 0.0

# ⚡ تمت استعادة الـ BoundingBox من أجل محرك الاصطدامات
@dataclass
class BoundingBox:
    x_min: float = 0.0
    y_min: float = 0.0
    z_min: float = 0.0
    x_max: float = 0.0
    y_max: float = 0.0
    z_max: float = 0.0

@dataclass
class Section:
    id: str
    origin_x: float
    origin_y: float
    origin_z: float
    width: float
    height: float
    depth: float
    is_active: bool = True
    children: list = field(default_factory=list)

# ⚡ تمت استعادة الاسم القديم من أجل محرك الحفظ (Serialization)
SectionTopology = Section

class CabinetTopologyManager:
    # ⚡ تمت استعادة التوقيع القديم، وتطبيق نصيحتك المعمارية بإنشاء ROOT فوراً
    def __init__(self, inner_width: float = 0.0, inner_height: float = 0.0, inner_depth: float = 0.0, **kwargs):
        self.w = inner_width
        self.h = inner_height
        self.d = inner_depth
        self.t = kwargs.get('thickness', 18.0)
        self.sections: Dict[str, Section] = {}
        if inner_width > 0 and inner_height > 0:
            self.seed_root(inner_width, inner_height, inner_depth)

    def get_section(self, section_id: str) -> Section:
        if section_id not in self.sections:
            raise KeyError(f"Section {section_id} not found.")
        return self.sections[section_id]

    def seed_root(self, width: float, height: float, depth: float):
        if "ROOT" not in self.sections:
            self.sections["ROOT"] = Section("ROOT", 0.0, 0.0, 0.0, width, height, depth)

    def add_vertical_divider(self, x_offset: float, divider_thickness: float, section_id: str = "ROOT") -> Tuple[str, str, str]:
        if section_id not in self.sections:
            raise KeyError(f"Section {section_id} not found. Must seed_root first.")
            
        parent = self.sections[section_id]
        div_uid = f"{section_id}_D_{int(x_offset)}"
        left_id = f"{section_id}_L_{int(x_offset)}"
        right_id = f"{section_id}_R_{int(x_offset)}"
        
        self.sections[left_id] = Section(
            id=left_id, origin_x=parent.origin_x, origin_y=parent.origin_y, origin_z=parent.origin_z,
            width=x_offset, height=parent.height, depth=parent.depth
        )
        
        right_start_x = parent.origin_x + x_offset + divider_thickness
        right_width = parent.width - x_offset - divider_thickness
        self.sections[right_id] = Section(
            id=right_id, origin_x=right_start_x, origin_y=parent.origin_y, origin_z=parent.origin_z,
            width=right_width, height=parent.height, depth=parent.depth
        )
        
        parent.children.extend([left_id, right_id])
        parent.is_active = False
             
        return div_uid, left_id, right_id

TopologyManager = CabinetTopologyManager
