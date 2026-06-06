from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class UnifiedManufacturingOperation:
    operation_type: str

    diameter: float = 0.0
    depth: float = 0.0

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    face: str = ""

    axis: str = "Z"

    source: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)
