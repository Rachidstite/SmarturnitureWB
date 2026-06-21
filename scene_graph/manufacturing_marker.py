from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class ManufacturingMarker:
    operation_type: str = ""
    target_node_id: str = ""
    visual_type: str = ""
    start_x: float = 0.0
    start_y: float = 0.0
    width: float = 0.0
    depth: float = 0.0
    length: float = 0.0
    face: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
