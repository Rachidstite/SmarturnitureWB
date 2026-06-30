from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ManufacturingDecision:
    status: str = "PASS"
    ready_for_production: bool = False
    blocking_reasons: tuple[str, ...] = field(default_factory=tuple)
    warning_reasons: tuple[str, ...] = field(default_factory=tuple)
    recommended_action: str = ""
    legacy_readiness_status: str = ""
    source: str = "manufacturing-decision"
