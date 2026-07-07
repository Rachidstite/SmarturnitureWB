from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActiveEngineeringState:
    family: str = ""
    specification: Any = None
    cabinet: Any = None
    scene_graph: Any = None
    metadata: dict = field(default_factory=dict)
    engineering_dirty: bool = False
    manufacturing_stale: bool = False
    cost_stale: bool = False
    commercial_stale: bool = False
