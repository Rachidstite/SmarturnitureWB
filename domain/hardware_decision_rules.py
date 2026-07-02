from __future__ import annotations

from dataclasses import replace

from domain.hardware_decision import HardwareCompatibilityStatus, HardwareDecision


def apply_minifix_validation_decision_rule(
    decision: HardwareDecision,
) -> HardwareDecision:
    evidence_refs = tuple(decision.decision.traceability.evidence_refs)
    minifix_refs = tuple(
        ref for ref in evidence_refs if ref.startswith("MinifixValidationReport:")
    )
    if not minifix_refs:
        return replace(decision)

    messages = tuple(decision.decision.validation_messages)
    message_text = " | ".join(messages)
    lower_messages = tuple(message.lower() for message in messages)

    blocking_markers = ("block", "blocked", "constraint", "invalid", "fail")
    review_markers = ("warn", "warning", "review", "risk")
    has_blocking_signal = any(
        marker in message for message in lower_messages for marker in blocking_markers
    )
    has_review_signal = any(
        marker in message for message in lower_messages for marker in review_markers
    )

    compatibility_status = decision.compatibility_status
    if has_blocking_signal:
        compatibility_status = HardwareCompatibilityStatus.BLOCKED
    elif has_review_signal and messages:
        compatibility_status = HardwareCompatibilityStatus.NEEDS_REVIEW

    quality_impact_note = decision.quality_impact_note
    if messages:
        quality_impact_note = message_text

    source_parts = [
        part
        for part in (
            decision.decision.traceability.source_component,
            decision.decision.traceability.source_rule,
            minifix_refs[0],
        )
        if part
    ]
    manufacturing_impact_note = decision.manufacturing_impact_note
    if source_parts:
        manufacturing_impact_note = "Minifix validation evidence: " + " | ".join(source_parts)

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
