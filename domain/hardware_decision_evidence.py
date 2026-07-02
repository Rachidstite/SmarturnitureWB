from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HardwareDecisionEvidence:
    evidence_id: str = ""
    placement_report_refs: tuple[str, ...] = field(default_factory=tuple)
    validation_report_refs: tuple[str, ...] = field(default_factory=tuple)
    compatibility_report_refs: tuple[str, ...] = field(default_factory=tuple)
    manufacturing_report_refs: tuple[str, ...] = field(default_factory=tuple)
    cost_report_refs: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    blocking_constraints: tuple[str, ...] = field(default_factory=tuple)
    source_rules: tuple[str, ...] = field(default_factory=tuple)
    source_components: tuple[str, ...] = field(default_factory=tuple)
    evidence_notes: tuple[str, ...] = field(default_factory=tuple)
