from dataclasses import dataclass


@dataclass(frozen=True)
class CanonicalCNCRow:
    panel_id: str
    panel_role: str
    operation_type: str
    face: str
    axis: str
    x: float
    y: float
    z: float
    diameter: float
    depth: float
    is_through: bool
    source: str
