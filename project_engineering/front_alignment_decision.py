from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FrontAlignmentDecision:
    status: str = "PASS"
    aligned_component_count: int = 0
    warning_count: int = 0
    violation_count: int = 0
    source: str = ""

