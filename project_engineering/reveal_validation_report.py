from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from domain.diagnostics import ConstraintViolation
from project_engineering.reveal_validation_decision import RevealValidationDecision
from project_engineering.reveal_validation_fact import RevealValidationFact


@dataclass(frozen=True)
class RevealValidationReport:
    facts: Tuple[RevealValidationFact, ...] = field(default_factory=tuple)
    decision: RevealValidationDecision = field(default_factory=RevealValidationDecision)
    violations: Tuple[ConstraintViolation, ...] = field(default_factory=tuple)
    target_reveal_mm: float = 2.0
    tolerance_mm: float = 0.5
    source: str = ""
