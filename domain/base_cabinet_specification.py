from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BaseCabinetSpecification:
    width_mm: float = 600.0
    height_mm: float = 720.0
    depth_mm: float = 580.0
    door_count: int = 2
    shelf_count: int = 1
    has_back_panel: bool = True
    edge_banding_required: bool = True
    toe_kick_required: bool = True
    hinge_family: str = "STANDARD_110"
    drawer_family: str = "NONE"
