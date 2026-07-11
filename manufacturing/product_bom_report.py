from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductBomRow:
    bom_category: str
    identity: str
    description: str
    quantity: int
    unit: str
    component_reference: tuple[str, ...]
    cabinet_reference: tuple[str, ...]
    source_reference: tuple[str, ...]
    material: str | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    thickness_mm: float | None = None
    component_role: str | None = None
    group: str | None = None


@dataclass(frozen=True)
class ProductBomReport:
    rows: tuple[ProductBomRow, ...] = ()
    warnings: tuple[str, ...] = ()
    source: str = ""
