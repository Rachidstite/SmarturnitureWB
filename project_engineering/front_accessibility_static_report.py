from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from domain.diagnostics import ConstraintViolation
from project_engineering.front_accessibility_static_decision import (
    FrontAccessibilityStaticDecision,
)
from project_engineering.front_accessibility_static_fact import (
    FrontAccessibilityStaticFact,
)


@dataclass(frozen=True)
class FrontAccessibilityStaticReport:
    facts: Tuple[FrontAccessibilityStaticFact, ...] = field(default_factory=tuple)
    decision: FrontAccessibilityStaticDecision = field(
        default_factory=FrontAccessibilityStaticDecision
    )
    violations: Tuple[ConstraintViolation, ...] = field(default_factory=tuple)
    tolerance_mm: float = 0.5
    source: str = ""
