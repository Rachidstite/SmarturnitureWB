from __future__ import annotations

from dataclasses import replace

from domain.hardware_decision import HardwareCompatibilityStatus, HardwareDecision
from domain.hardware_decision_semantic_normalization import (
    normalize_hardware_decision_semantics,
)


def apply_compatibility_decision_rule(
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
    if normalized.is_blocked or normalized.status == "BLOCKED":
        compatibility_status = HardwareCompatibilityStatus.BLOCKED
    elif normalized.status in {"WARNING", "NEEDS_REVIEW", "RISK"} and messages:
        compatibility_status = HardwareCompatibilityStatus.NEEDS_REVIEW

    quality_impact_note = decision.quality_impact_note
    if messages:
        quality_impact_note = " | ".join(messages)

    source_parts = [
        part
        for part in (
            decision.decision.traceability.source_component,
            decision.decision.traceability.source_rule,
            normalized.source_ref,
        )
        if part
    ]
    manufacturing_impact_note = decision.manufacturing_impact_note
    if source_parts:
        manufacturing_impact_note = "Compatibility evidence: " + " | ".join(source_parts)

    replacement_reason = decision.replacement_reason
    replacement_messages = tuple(
        message
        for message in messages
        if "replace" in message.lower() or "replacement" in message.lower()
    )
    if replacement_messages:
        replacement_reason = " | ".join(replacement_messages)

    return replace(
        decision,
        compatibility_status=compatibility_status,
        quality_impact_note=quality_impact_note,
        manufacturing_impact_note=manufacturing_impact_note,
        replacement_reason=replacement_reason,
    )
