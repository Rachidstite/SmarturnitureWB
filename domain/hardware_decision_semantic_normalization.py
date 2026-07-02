from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedHardwareDecisionSemantics:
    status: str = ""
    severity: str = ""
    is_blocked: bool = False
    used_text_fallback: bool = False
    source_type: str = ""
    source_ref: str = ""


def normalize_hardware_decision_semantics(signals) -> NormalizedHardwareDecisionSemantics:
    source_type = str(signals.get("source_type", ""))
    source_ref = str(signals.get("source_ref", ""))
    semantic_fields = dict(signals.get("semantic_fields", {}) or {})
    messages = tuple(str(message) for message in (signals.get("messages", ()) or ()))

    status = ""
    severity = ""
    is_blocked = False
    used_text_fallback = False

    decision_status = str(semantic_fields.get("decision_status", "")).upper()
    validation_status = str(semantic_fields.get("validation_status", "")).upper()
    requires_review = bool(semantic_fields.get("requires_review", False))
    explicit_blocked = bool(semantic_fields.get("is_blocked", False))
    blocking_issue_count = int(semantic_fields.get("blocking_issue_count", 0) or 0)
    warning_count = int(semantic_fields.get("warning_count", 0) or 0)
    is_valid = semantic_fields.get("is_valid", None)
    hardware_risk = str(semantic_fields.get("hardware_risk", "")).upper()
    placement_quality = str(semantic_fields.get("placement_quality", "")).upper()

    if explicit_blocked or blocking_issue_count > 0:
        status = "BLOCKED"
        is_blocked = True
    elif requires_review:
        status = "NEEDS_REVIEW"
    elif decision_status:
        if decision_status == "REVIEW_REQUIRED":
            status = "NEEDS_REVIEW"
        else:
            status = decision_status
        is_blocked = status == "BLOCKED"
    elif validation_status:
        status = validation_status
        is_blocked = status == "BLOCKED"
    elif is_valid is not None:
        status = "VALID" if bool(is_valid) else "INVALID"
    elif warning_count > 0:
        status = "WARNING"
    elif hardware_risk or placement_quality:
        status = "RISK"

    if hardware_risk in {"HIGH", "MEDIUM", "LOW"} or placement_quality in {
        "POOR",
        "UNKNOWN",
        "GOOD",
        "EXCELLENT",
    }:
        severity = "RISK"

    if not status and messages:
        used_text_fallback = True
        message_blob = " | ".join(messages).lower()
        if any(token in message_blob for token in ("block", "blocked", "invalid", "fail")):
            status = "BLOCKED"
            is_blocked = True
        elif any(token in message_blob for token in ("warn", "warning")):
            status = "WARNING"
        elif "review" in message_blob:
            status = "NEEDS_REVIEW"
        elif "risk" in message_blob:
            status = "RISK"

    return NormalizedHardwareDecisionSemantics(
        status=status,
        severity=severity,
        is_blocked=is_blocked,
        used_text_fallback=used_text_fallback,
        source_type=source_type,
        source_ref=source_ref,
    )
