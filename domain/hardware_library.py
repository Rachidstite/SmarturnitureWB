from dataclasses import dataclass, field
from typing import List, Dict
from domain.anchors import MountFace

@dataclass
class HoleSpec:
    diameter: float
    depth: float
    face: MountFace = MountFace.FRONT
    axis: str = "Z"                   # CNC Machining Axis
    offset_x: float = 0.0
    offset_y: float = 0.0
    is_through_hole: bool = False

@dataclass
class HardwareSpec:
    sku: str
    manufacturer: str
    model: str
    revision: str
    category: str
    host_holes: List[HoleSpec] = field(default_factory=list)
    target_holes: List[HoleSpec] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        """The single source of truth for UI and BOM naming"""
        return f"{self.manufacturer} {self.model}"

class HardwareRegistry:
    def __init__(self):
        self._catalog: Dict[str, HardwareSpec] = {}
        self._seed_catalog()

    def get_hardware(self, sku: str) -> HardwareSpec:
        return self._catalog.get(sku)

    def _seed_catalog(self):
        self._catalog["HINGE_BLUM_110_V1"] = HardwareSpec(
            sku="HINGE_BLUM_110_V1", manufacturer="BLUM", model="CLIP_TOP_110", revision="1.0", category="HINGES",
            host_holes=[
                HoleSpec(diameter=5, depth=12, face=MountFace.LEFT, offset_x=37, offset_y=16),
                HoleSpec(diameter=5, depth=12, face=MountFace.LEFT, offset_x=37, offset_y=-16)
            ],
            target_holes=[
                HoleSpec(diameter=35, depth=12.5, face=MountFace.BACK, offset_x=22, offset_y=0),
                HoleSpec(diameter=2.5, depth=10, face=MountFace.BACK, offset_x=22-9.5, offset_y=22.5),
                HoleSpec(diameter=2.5, depth=10, face=MountFace.BACK, offset_x=22-9.5, offset_y=-22.5)
            ]
        )
        self._catalog["MINIFIX_15_V1"] = HardwareSpec(
            sku="MINIFIX_15_V1", manufacturer="HAFELE", model="MINIFIX_15", revision="1.0", category="CONNECTORS",
            host_holes=[HoleSpec(diameter=5, depth=12, face=MountFace.LEFT, offset_x=0, offset_y=0)],
            target_holes=[
                HoleSpec(diameter=15, depth=14, face=MountFace.FRONT, offset_x=34, offset_y=0),
                HoleSpec(diameter=8, depth=34, face=MountFace.LEFT, axis="X", offset_x=0, offset_y=0)
            ]
        )
        self._catalog["CONFIRMAT_50_V1"] = HardwareSpec(
            sku="CONFIRMAT_50_V1", manufacturer="GENERIC", model="CONFIRMAT_5x50", revision="1.0", category="CONNECTORS",
            host_holes=[HoleSpec(diameter=7, depth=18, face=MountFace.LEFT, is_through_hole=True)],
            target_holes=[HoleSpec(diameter=5, depth=34, face=MountFace.LEFT, axis="X")]
        )
        self._catalog["SHELF_PIN_5MM"] = HardwareSpec(
            sku="SHELF_PIN_5MM", manufacturer="GENERIC", model="STEEL_PIN_5MM", revision="1.0", category="ACCESSORIES",
            host_holes=[HoleSpec(diameter=5, depth=12, face=MountFace.LEFT, is_through_hole=False)],
            target_holes=[]
        )
