from __future__ import annotations

from dataclasses import replace

from domain.hardware_decision import HardwareCompatibilityStatus, HardwareDecision
from domain.hardware_decision_semantic_normalization import (
    normalize_hardware_decision_semantics,
)


def apply_quality_decision_rule(
    decision: HardwareDecision,
) -> HardwareDecision:
    evidence_refs = tuple(decision.decision.traceability.evidence_refs)
    if not evidence_refs:
        return replace(decision)

    source_ref = evidence_refs[0]
    source_type = source_ref.split(":", 1)[0] if ":" in source_ref else source_ref
    messages = tuple(decision.decision.validation_messages)
    normalized = normalize_hardware_decision_semantics(
        {
            "source_type": source_type,
            "source_ref": source_ref,
            "semantic_fields": {},
            "messages": messages,
        }
    )

    compatibility_status = decision.compatibility_status
    if normalized.is_blocked or normalized.status in {"BLOCKED", "INVALID"}:
        compatibility_status = HardwareCompatibilityStatus.BLOCKED

    quality_impact_note = decision.quality_impact_note
    if normalized.status in {"BLOCKED", "INVALID", "WARNING", "NEEDS_REVIEW", "RISK"}:
        note_parts = ["Quality evidence", normalized.status]
        if decision.decision.traceability.source_component:
            note_parts.append(decision.decision.traceability.source_component)
        if decision.decision.traceability.source_rule:
            note_parts.append(decision.decision.traceability.source_rule)
        quality_impact_note = ": ".join(note_parts[:2])
        if len(note_parts) > 2:
            quality_impact_note += " | " + " | ".join(note_parts[2:])
        if messages:
            quality_impact_note += " | " + " | ".join(messages)

    return replace(
        decision,
        compatibility_status=compatibility_status,
        quality_impact_note=quality_impact_note,
    )
