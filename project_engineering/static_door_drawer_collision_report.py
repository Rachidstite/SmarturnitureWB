from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from domain.diagnostics import ConstraintViolation
from project_engineering.static_door_drawer_collision_decision import (
    StaticDoorDrawerCollisionDecision,
)
from project_engineering.static_door_drawer_collision_fact import (
    StaticDoorDrawerCollisionFact,
)


@dataclass(frozen=True)
class StaticDoorDrawerCollisionReport:
    facts: Tuple[StaticDoorDrawerCollisionFact, ...] = field(default_factory=tuple)
    decision: StaticDoorDrawerCollisionDecision = field(
        default_factory=StaticDoorDrawerCollisionDecision
    )
    violations: Tuple[ConstraintViolation, ...] = field(default_factory=tuple)
    tolerance_mm: float = 0.5
    source: str = ""
