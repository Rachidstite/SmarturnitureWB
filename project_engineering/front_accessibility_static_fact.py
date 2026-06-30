from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FrontAccessibilityStaticFact:
    component_id: str
    component_type: str
    section_id: str
    x_mm: float
    y_mm: float
    z_mm: float
    width_mm: float
    height_mm: float
    depth_or_thickness_mm: float
    source: str = ""
