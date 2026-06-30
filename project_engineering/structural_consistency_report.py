from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from domain.diagnostics import ConstraintViolation
from project_engineering.structural_consistency_decision import (
    StructuralConsistencyDecision,
)
from project_engineering.structural_consistency_fact import StructuralConsistencyFact


@dataclass(frozen=True)
class StructuralConsistencyReport:
    facts: Tuple[StructuralConsistencyFact, ...] = field(default_factory=tuple)
    decision: StructuralConsistencyDecision = field(
        default_factory=StructuralConsistencyDecision
    )
    violations: Tuple[ConstraintViolation, ...] = field(default_factory=tuple)
    source: str = ""
