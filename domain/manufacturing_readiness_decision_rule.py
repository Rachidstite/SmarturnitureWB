from __future__ import annotations

from dataclasses import replace

from domain.hardware_decision import HardwareCompatibilityStatus, HardwareDecision
from domain.hardware_decision_semantic_normalization import (
    normalize_hardware_decision_semantics,
)


def apply_manufacturing_readiness_decision_rule(
    decision: HardwareDecision,
) -> HardwareDecision:
    evidence_refs = tuple(decision.decision.traceability.evidence_refs)
    if not evidence_refs:
        return replace(decision)

    source_ref = evidence_refs[0]
    source_type = source_ref.split(":", 1)[0] if ":" in source_ref else source_ref
    normalized = normalize_hardware_decision_semantics(
        {
            "source_type": source_type,
            "source_ref": source_ref,
            "semantic_fields": {},
            "messages": tuple(decision.decision.validation_messages),
        }
    )

    compatibility_status = decision.compatibility_status
    if normalized.is_blocked or normalized.status == "BLOCKED":
        compatibility_status = HardwareCompatibilityStatus.BLOCKED

    manufacturing_impact_note = decision.manufacturing_impact_note
    if normalized.status:
        note_parts = ["Manufacturing readiness", normalized.status]
        if decision.decision.traceability.source_component:
            note_parts.append(decision.decision.traceability.source_component)
        if decision.decision.traceability.source_rule:
            note_parts.append(decision.decision.traceability.source_rule)
        manufacturing_impact_note = ": ".join(note_parts[:2])
        if len(note_parts) > 2:
            manufacturing_impact_note += " | " + " | ".join(note_parts[2:])

    return replace(
        decision,
        compatibility_status=compatibility_status,
        manufacturing_impact_note=manufacturing_impact_note,
    )
