from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HardwareDecisionContext:
    context_id: str = ""
    product_family: str = ""
    cabinet_type: str = ""
    material_type: str = ""
    panel_thickness_mm: float = 0.0
    cabinet_width_mm: float = 0.0
    cabinet_height_mm: float = 0.0
    cabinet_depth_mm: float = 0.0
    mounting_type: str = ""
    required_load_kg: float = 0.0
    available_hardware_skus: tuple[str, ...] = field(default_factory=tuple)
    manufacturing_capabilities: tuple[str, ...] = field(default_factory=tuple)
    customer_constraints: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)
