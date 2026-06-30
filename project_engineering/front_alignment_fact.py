from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FrontAlignmentFact:
    component_id: str
    component_type: str
    section_id: str
    component_index: int
    x_mm: float
    y_mm: float
    z_mm: float
    width_mm: float
    height_mm: float
    front_plane_mm: float
    source: str = ""

