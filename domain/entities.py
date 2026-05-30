from dataclasses import dataclass, field
from typing import Dict, List, Optional
from domain.core_types import NodeRole, MachiningOperation
from domain.topology import Transform3D

@dataclass
class Identity:
    key: str

@dataclass
class SceneNode:
    identity: Identity
    role: NodeRole
    width: float
    height: float
    thickness: float
    material: str
    edge_bands: Dict[str, str]
    category: str = "PANEL"
    transform: Transform3D = field(default_factory=Transform3D)
    machining_ops: List[MachiningOperation] = field(default_factory=list)
