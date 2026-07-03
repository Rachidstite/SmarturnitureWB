from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DecisionProjectionSection:
    source_object: object = None
    source_field: str = ""
    source_value: object = None
    meaning: str = ""
    user_decision_supported: str = ""


@dataclass(frozen=True)
class FactoryDecisionProjection:
    readiness_summary: DecisionProjectionSection = field(
        default_factory=DecisionProjectionSection
    )
    blocking_issues: tuple[DecisionProjectionSection, ...] = field(
        default_factory=tuple
    )
    warning_summary: DecisionProjectionSection = field(
        default_factory=DecisionProjectionSection
    )
    manufacturing_output_status: tuple[DecisionProjectionSection, ...] = field(
        default_factory=tuple
    )
    assembly_status: DecisionProjectionSection = field(
        default_factory=DecisionProjectionSection
    )
    commercial_status: DecisionProjectionSection = field(
        default_factory=DecisionProjectionSection
    )
    visualization_status: DecisionProjectionSection | None = None
    recommended_next_actions: tuple[str, ...] = field(default_factory=tuple)
    release_decision: DecisionProjectionSection = field(
        default_factory=DecisionProjectionSection
    )
