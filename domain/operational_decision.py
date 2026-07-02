from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class OperationalDecisionType(str, Enum):
    HARDWARE = "HARDWARE"
    ASSEMBLY = "ASSEMBLY"
    MACHINING = "MACHINING"
    MATERIAL = "MATERIAL"
    COST = "COST"
    OPTIMIZATION = "OPTIMIZATION"
    PACKAGING = "PACKAGING"
    SHIPPING = "SHIPPING"
    QUALITY = "QUALITY"


class OperationalDecisionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class OperationalDecisionOption:
    option_id: str = ""
    label: str = ""
    description: str = ""
    estimated_cost_impact: float = 0.0
    estimated_time_impact: float = 0.0
    estimated_quality_impact: float = 0.0
    risk_level: str = ""
    is_selected: bool = False


@dataclass(frozen=True)
class OperationalDecisionImpact:
    engineering_impact: float = 0.0
    manufacturing_impact: float = 0.0
    cost_impact: float = 0.0
    quality_impact: float = 0.0
    automation_impact: float = 0.0
    waste_impact: float = 0.0


@dataclass(frozen=True)
class OperationalDecisionTraceability:
    source_component: str = ""
    source_report: str = ""
    source_rule: str = ""
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class OperationalDecision:
    decision_id: str = ""
    decision_type: OperationalDecisionType = OperationalDecisionType.HARDWARE
    status: OperationalDecisionStatus = OperationalDecisionStatus.PROPOSED
    selected_option: OperationalDecisionOption | None = None
    candidate_options: tuple[OperationalDecisionOption, ...] = field(default_factory=tuple)
    reason: str = ""
    impact: OperationalDecisionImpact = field(default_factory=OperationalDecisionImpact)
    traceability: OperationalDecisionTraceability = field(
        default_factory=OperationalDecisionTraceability
    )
    validation_messages: tuple[str, ...] = field(default_factory=tuple)
