from dataclasses import dataclass, field
from typing import Dict, List
from .enums import DrawerLayoutMode
@dataclass
class SectionConfig:
    drawers: int = 0; shelves: int = 0; doors: str = "None"
    door_count: int = 2; drawer_type: str = "Inset"
    drawer_heights: List[float] = field(default_factory=list)
    drawer_layout_mode: DrawerLayoutMode = DrawerLayoutMode.MANUAL
@dataclass
class CabinetParams:
    width: float = 1800.0; height: float = 2200.0; depth: float = 600.0
    base_height: float = 80.0; sec_count: int = 3
    sec_data: Dict[int, SectionConfig] = field(default_factory=dict)
    cnc_mode: bool = False; hw_mode: bool = False
    back_thickness: float = 8.0; drawer_depth: float = 450.0; drawer_bottom_thickness: float = 8.0

    hinge_sku: str = "HINGE_BLUM_110_V1"
    slide_sku: str = "DRAWER_SLIDE_SOFTCLOSE_450"
    handle_sku: str = "HANDLE_128_BLACK"
