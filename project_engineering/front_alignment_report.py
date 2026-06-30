from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from domain.diagnostics import ConstraintViolation
from project_engineering.front_alignment_decision import FrontAlignmentDecision
from project_engineering.front_alignment_fact import FrontAlignmentFact


@dataclass(frozen=True)
class FrontAlignmentReport:
    facts: Tuple[FrontAlignmentFact, ...] = field(default_factory=tuple)
    decision: FrontAlignmentDecision = field(default_factory=FrontAlignmentDecision)
    violations: Tuple[ConstraintViolation, ...] = field(default_factory=tuple)
    tolerance_mm: float = 0.5
    source: str = ""

