from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StaticDoorDrawerCollisionDecision:
    status: str = "PASS"
    checked_pair_count: int = 0
    warning_count: int = 0
    violation_count: int = 0
    source: str = ""
