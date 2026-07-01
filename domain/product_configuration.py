from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ProductConfiguration:
    family_id: str
    width: float
    height: float
    depth: float
    material: str = "MDF"
    options: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not str(self.family_id or "").strip():
            raise ValueError("family_id is required")
        if float(self.width) <= 0:
            raise ValueError("width must be greater than 0")
        if float(self.height) <= 0:
            raise ValueError("height must be greater than 0")
        if float(self.depth) <= 0:
            raise ValueError("depth must be greater than 0")
        if not str(self.material or "").strip():
            raise ValueError("material is required")
