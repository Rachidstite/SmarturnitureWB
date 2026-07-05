# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Operational Intelligence
# Production Decision Read Model
#
# Summarizes whether production should proceed based on FOI-1/2/3 outputs.
#
# Follows ADR-FOI-4: Production Decision is a Read Model / Decision Record.
# It does NOT execute production, schedule jobs, or make final approvals.
#
# This module is:
# - deterministic and side-effect free
# - purely a read model builder
# - consumes only FOI-1/2/3 — no domain imports
# - no engine, workflow, or service
# - no calculations
# - no decisions (advisory only)
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ── Decision status constants ─────────────────────────────────────────

START_READY = "START_READY"
START_AFTER_REVIEW = "START_AFTER_REVIEW"
HOLD = "HOLD"
BLOCKED = "BLOCKED"
UNKNOWN = "UNKNOWN"

# ── Confidence mapping ───────────────────────────────────────────────

_HIGH = "HIGH"
_MEDIUM = "MEDIUM"
_LOW = "LOW"
_NONE = "NONE"

_CONFIDENCE_ORDER = {
    _NONE: 0,
    _LOW: 1,
    _MEDIUM: 2,
    _HIGH: 3,
}


@dataclass(frozen=True)
class ProductionDecisionReason:
    """A single reason contributing to the production decision.

    Attributes:
        reason_text: Human-readable explanation.
        blocking_item_id: Optional reference to the source blocking item.
        recommendation_id: Optional reference to the source recommendation.
    """

    reason_text: str = ""
    blocking_item_id: str = ""
    recommendation_id: str = ""


@dataclass(frozen=True)
class ProductionDecisionReadModel:
    """Read-only production decision record.

    Attributes:
        decision_status: START_READY, START_AFTER_REVIEW, HOLD, BLOCKED, or UNKNOWN.
        decision_reasons: All contributing reasons with traceability.
        blocking_item_ids: All referenced blocking item IDs.
        recommendation_ids: All referenced recommendation IDs.
        confidence: Aggregate confidence (HIGH, MEDIUM, LOW, NONE).
        summary_message: Human-readable one-line summary.
    """

    decision_status: str = UNKNOWN
    decision_reasons: tuple[ProductionDecisionReason, ...] = field(default_factory=tuple)
    blocking_item_ids: tuple[str, ...] = field(default_factory=tuple)
    recommendation_ids: tuple[str, ...] = field(default_factory=tuple)
    confidence: str = _NONE
    summary_message: str = ""


def _resolve_confidence(
    recommendations_model: Any,
) -> str:
    """Resolve the aggregate confidence from a recommendation read model.

    Returns the lowest confidence found, or NONE if no recommendations exist.
    """
    recs = getattr(recommendations_model, "recommendations", ()) or ()
    if not recs:
        return _NONE

    lowest = _HIGH
    for rec in recs:
        conf = getattr(rec, "confidence", _NONE) or _NONE
        if _CONFIDENCE_ORDER.get(conf, 0) < _CONFIDENCE_ORDER.get(lowest, 0):
            lowest = conf
    return lowest


def _build_blocked_summary(
    reasons: list[ProductionDecisionReason],
    blocking_item_ids: tuple[str, ...],
    recommendation_ids: tuple[str, ...],
) -> str:
    """Build a summary for BLOCKED status."""
    parts = [f"Production decision: {BLOCKED}"]
    count = len(blocking_item_ids)
    if count > 0:
        parts.append(f"{count} unresolved blocker(s)")
    return " — ".join(parts)


def _build_summary(
    status: str,
    reasons: list[ProductionDecisionReason],
    blocking_item_ids: tuple[str, ...],
    recommendation_ids: tuple[str, ...],
    confidence: str,
) -> str:
    """Build a human-readable summary message."""
    if status == BLOCKED:
        return _build_blocked_summary(reasons, blocking_item_ids, recommendation_ids)

    parts = [f"Production decision: {status}"]
    if len(blocking_item_ids) > 0:
        parts.append(f"{len(blocking_item_ids)} blocking reference(s)")
    if len(recommendation_ids) > 0:
        parts.append(f"{len(recommendation_ids)} recommendation(s)")
    parts.append(f"confidence: {confidence}")
    return " — ".join(parts)


def _collect_traceability(
    blocking_analysis: Any,
    recommendations: Any,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Collect blocking_item_ids and recommendation_ids from inputs.

    Returns (blocking_item_ids, recommendation_ids).
    """
    blocking_ids: list[str] = []
    rec_ids: list[str] = []

    items = getattr(blocking_analysis, "blocking_items", ()) or ()
    for item in items:
        bid = getattr(item, "blocking_item_id", "") or ""
        if bid:
            blocking_ids.append(bid)

    recs = getattr(recommendations, "recommendations", ()) or ()
    for rec in recs:
        rid = getattr(rec, "recommendation_id", "") or ""
        if rid:
            rec_ids.append(rid)

    return tuple(blocking_ids), tuple(rec_ids)


def _build_reasons(
    status: str,
    readiness: Any,
    blocking_analysis: Any,
    recommendations: Any,
    blocking_item_ids: tuple[str, ...],
    recommendation_ids: tuple[str, ...],
) -> list[ProductionDecisionReason]:
    """Build decision reasons based on the resolved status."""
    reasons: list[ProductionDecisionReason] = []

    # Always include readiness status reason
    readiness_status = getattr(readiness, "status", "") or ""
    if readiness_status:
        reasons.append(ProductionDecisionReason(
            reason_text=f"Factory readiness: {readiness_status}",
        ))

    # Include blocking item reasons
    items = getattr(blocking_analysis, "blocking_items", ()) or ()
    # Only add reasons for items that contributed to the decision
    for item in items:
        bid = getattr(item, "blocking_item_id", "") or ""
        if not bid:
            continue
        severity = getattr(item, "severity", "") or ""
        human_message = getattr(item, "human_message", "") or ""

        # Only include items that match the current severity level or above
        # For BLOCKED: include BLOCKED severity items
        # For HOLD: include ERROR severity items
        # For START_AFTER_REVIEW: include WARNING items
        if status == BLOCKED:
            if severity in ("BLOCKED", "ERROR"):
                reasons.append(ProductionDecisionReason(
                    reason_text=human_message,
                    blocking_item_id=bid,
                ))
        elif status == HOLD:
            if severity in ("ERROR", "WARNING"):
                reasons.append(ProductionDecisionReason(
                    reason_text=human_message,
                    blocking_item_id=bid,
                ))
        elif status == START_AFTER_REVIEW:
            if severity == "WARNING":
                reasons.append(ProductionDecisionReason(
                    reason_text=human_message,
                    blocking_item_id=bid,
                ))

    # Include recommendation reasons
    recs = getattr(recommendations, "recommendations", ()) or ()
    for rec in recs:
        rid = getattr(rec, "recommendation_id", "") or ""
        if not rid:
            continue
        rec_conf = getattr(rec, "confidence", _NONE) or _NONE
        human_msg = getattr(rec, "human_message", "") or ""
        responsible = getattr(rec, "responsible_domain", "") or ""

        # Include recommendations that match the decision context
        if status in (BLOCKED, HOLD) and rec_conf in (_HIGH, _MEDIUM):
            reasons.append(ProductionDecisionReason(
                reason_text=f"[{responsible}] {human_msg}",
                recommendation_id=rid,
            ))
        elif status == START_AFTER_REVIEW and rec_conf == _MEDIUM:
            reasons.append(ProductionDecisionReason(
                reason_text=f"[{responsible}] {human_msg}",
                recommendation_id=rid,
            ))

    return reasons


def _determine_status(
    readiness: Any,
    blocking_analysis: Any,
) -> str:
    """Determine the decision status from readiness and blocking analysis.

    Follows ADR-FOI-4 Appendix A status decision table.
    Priority is top-to-bottom: first matching row determines status.
    """
    readiness_status = getattr(readiness, "status", "") or ""

    # Row 1: BLOCKED if readiness is BLOCKED
    if readiness_status in (BLOCKED,):
        return BLOCKED

    # Row 2: BLOCKED if critical_count > 0
    critical_count = getattr(blocking_analysis, "critical_count", 0) or 0
    if critical_count > 0:
        return BLOCKED

    # Row 3: HOLD if NOT_READY and no critical blockers
    if readiness_status in ("NOT_READY",):
        return HOLD

    # Row 4: HOLD if high_count > 0 and critical_count == 0
    high_count = getattr(blocking_analysis, "high_count", 0) or 0
    if high_count > 0:
        return HOLD

    # Row 5: START_AFTER_REVIEW if medium_count > 0
    medium_count = getattr(blocking_analysis, "medium_count", 0) or 0
    if medium_count > 0:
        return START_AFTER_REVIEW

    # Row 6: READY if readiness is READY and no blockers/errors/warnings
    if readiness_status in ("READY",):
        return START_READY

    # Row 7: UNKNOWN if UNKNOWN or no data
    return UNKNOWN


def build_production_decision_read_model(
    readiness: Any = None,
    blocking_analysis: Any = None,
    recommendations: Any = None,
) -> ProductionDecisionReadModel:
    """Build a ProductionDecisionReadModel from FOI-1/2/3 outputs.

    Accepts:
    - readiness: A FactoryReadinessReadModel (or None)
    - blocking_analysis: A FactoryBlockingAnalysisReadModel (or None)
    - recommendations: A FactoryRecommendationReadModel (or None)

    Determines the production decision status following ADR-FOI-4 rules:
    BLOCKED → HOLD → START_AFTER_REVIEW → START_READY → UNKNOWN.

    The function is deterministic and side-effect free. It never:
    - executes production
    - schedules jobs
    - generates CNC
    - approves quotations
    - calculates cost or geometry
    - uses AI
    """
    if readiness is None or blocking_analysis is None or recommendations is None:
        return ProductionDecisionReadModel(
            decision_status=UNKNOWN,
            confidence=_NONE,
            summary_message="Production decision: UNKNOWN — missing FOI data",
        )

    # Determine status
    decision_status = _determine_status(readiness, blocking_analysis)

    # Collect traceability
    blocking_item_ids, recommendation_ids = _collect_traceability(
        blocking_analysis, recommendations,
    )

    # Resolve confidence
    confidence = _resolve_confidence(recommendations)

    # Build reasons
    decision_reasons = _build_reasons(
        decision_status, readiness, blocking_analysis, recommendations,
        blocking_item_ids, recommendation_ids,
    )

    # Build summary
    summary_message = _build_summary(
        decision_status, decision_reasons, blocking_item_ids,
        recommendation_ids, confidence,
    )

    return ProductionDecisionReadModel(
        decision_status=decision_status,
        decision_reasons=tuple(decision_reasons),
        blocking_item_ids=blocking_item_ids,
        recommendation_ids=recommendation_ids,
        confidence=confidence,
        summary_message=summary_message,
    )


__all__ = [
    "START_READY",
    "START_AFTER_REVIEW",
    "HOLD",
    "BLOCKED",
    "UNKNOWN",
    "ProductionDecisionReason",
    "ProductionDecisionReadModel",
    "build_production_decision_read_model",
]
