from __future__ import annotations

from dataclasses import replace

from domain.compatibility_decision_rule import apply_compatibility_decision_rule
from domain.hardware_decision import HardwareDecision


def apply_minifix_validation_decision_rule(
    decision: HardwareDecision,
) -> HardwareDecision:
    # Delegate to the shared compatibility path, which uses
    # normalize_hardware_decision_semantics(...) for interpretation.
    evidence_refs = tuple(decision.decision.traceability.evidence_refs)
    minifix_refs = tuple(
        ref for ref in evidence_refs if ref.startswith("MinifixValidationReport:")
    )
    if not minifix_refs:
        return replace(decision)
    return apply_compatibility_decision_rule(decision)
