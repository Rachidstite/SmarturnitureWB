from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class _WallPanelGeometryRecord:
    placement_key: str
    role: str
    width_mm: float
    depth_mm: float
    height_mm: float
    origin_mm: Tuple[float, float, float]


def _read(subject, key: str):
    if isinstance(subject, dict):
        return subject[key]
    return getattr(subject, key)


def _build_record(placements, placement_key: str) -> _WallPanelGeometryRecord:
    placement = _read(placements, placement_key)
    return _WallPanelGeometryRecord(
        placement_key=placement_key,
        role=_read(placement, "role"),
        width_mm=_read(placement, "width_mm"),
        depth_mm=_read(placement, "depth_mm"),
        height_mm=_read(placement, "height_mm"),
        origin_mm=_read(placement, "position_mm"),
    )


def build_wall_panel_geometry(placements) -> Tuple[_WallPanelGeometryRecord, ...]:
    ordered_panel_keys: Iterable[str] = tuple(_read(placements, "ordered_panel_keys"))
    return tuple(_build_record(placements, placement_key) for placement_key in ordered_panel_keys)
