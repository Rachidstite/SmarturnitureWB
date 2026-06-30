from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StaticDoorDrawerCollisionFact:
    component_id: str
    component_type: str
    section_id: str
    x_mm: float
    y_mm: float
    z_mm: float
    width_mm: float
    thickness_mm: float
    height_mm: float
    source: str = ""
