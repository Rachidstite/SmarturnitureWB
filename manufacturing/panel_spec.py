from dataclasses import dataclass, field
from typing import Any, Dict, List

from shared.roles import NodeRole
from manufacturing.edge_spec import EdgeSpec


@dataclass
class PanelSpec:
    """Engineering-ready panel specification."""

    identity: str
    role: NodeRole

    width: float
    height: float
    thickness: float
    material: str

    span: float = 0.0

    section_width: float = 0.0

    supported_edges: int = 2

    load_class: str = "normal"

    panel_category: str = "generic"

    metadata: Dict[str, Any] = field(default_factory=dict)

    grain_direction: str = "NONE"

    edge_spec: EdgeSpec = field(default_factory=EdgeSpec)

    quantity: int = 1

    group: str = ""

    cnc_operations: List[str] = field(default_factory=list)
