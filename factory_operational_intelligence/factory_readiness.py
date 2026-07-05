# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Operational Intelligence
# Factory Readiness Read Model
#
# Determines whether a project is ready for factory manufacturing
# by analyzing existing ReviewPanelReadModel data from all 5 review
# domains: Validation, Manufacturing, Cost, Commercial, Release.
#
# This module is:
# - deterministic and side-effect free
# - purely a read model builder — no engine, workflow, or service
# - consumes only CV2-native read models — no domain imports
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ── Status constants ──────────────────────────────────────────────────

READY = "READY"
NOT_READY = "NOT_READY"
NEEDS_REVIEW = "NEEDS_REVIEW"
BLOCKED = "BLOCKED"
UNKNOWN = "UNKNOWN"

# ── Severity constants ────────────────────────────────────────────────

_SEVERITY_BLOCKED = "BLOCKED"
_SEVERITY_ERROR = "ERROR"
_SEVERITY_WARNING = "WARNING"
_SEVERITY_INFO = "INFO"

# ── Status priority order (highest first) ─────────────────────────────

_STATUS_PRIORITY = {
    BLOCKED: 4,
    NOT_READY: 3,
    NEEDS_REVIEW: 2,
    READY: 1,
    UNKNOWN: 0,
}

# ── Severity priority (for classifying row values) ────────────────────

_SEVERITY_PRIORITY = {
    _SEVERITY_BLOCKED: 4,
    _SEVERITY_ERROR: 3,
    _SEVERITY_WARNING: 2,
    _SEVERITY_INFO: 1,
}

# ── Keyword patterns for section-based classification ─────────────────

_BLOCKED_SECTION_KEYWORDS = frozenset({
    "blocked", "blocker", "blocking",
})

_ERROR_SECTION_KEYWORDS = frozenset({
    "failed", "errors", "error", "fail",
})

_WARNING_SECTION_KEYWORDS = frozenset({
    "warnings", "warning",
})

_READY_SECTION_KEYWORDS = frozenset({
    "passed", "ready", "approvals", "released", "done",
})

# ── Keyword patterns for row-value-based classification ───────────────

_BLOCKED_VALUE_KEYWORDS = frozenset({
    "blocked", "blocker",
})

_ERROR_VALUE_KEYWORDS = frozenset({
    "fail", "error",
})

_WARNING_VALUE_KEYWORDS = frozenset({
    "warning", "pending", "needs review", "needs_review", "check",
})

_READY_VALUE_KEYWORDS = frozenset({
    "pass", "ready", "approved", "released", "done", "complete", "confirmed",
})


@dataclass(frozen=True)
class FactoryReadinessReason:
    """A single reason contributing to the factory readiness decision.

    Attributes:
        reason_text: Human-readable explanation.
        source_panel: The ReviewPanelReadModel panel_name that produced this reason.
        severity: One of BLOCKED, ERROR, WARNING, or INFO.
    """

    reason_text: str = ""
    source_panel: str = ""
    severity: str = _SEVERITY_INFO


@dataclass(frozen=True)
class FactoryReadinessReadModel:
    """Read-only assessment of factory manufacturing readiness.

    Attributes:
        status: One of READY, NOT_READY, NEEDS_REVIEW, BLOCKED, UNKNOWN.
        reasons: All contributing reasons with source panel and severity.
        blocking_count: Number of blocking/blocked findings.
        warning_count: Number of warning/review-needed findings.
        ready_count: Number of ready/pass findings.
        source_panels: Tuple of panel names that contributed data.
        summary_message: Human-readable one-line summary.
    """

    status: str = UNKNOWN
    reasons: tuple[FactoryReadinessReason, ...] = field(default_factory=tuple)
    blocking_count: int = 0
    warning_count: int = 0
    ready_count: int = 0
    source_panels: tuple[str, ...] = field(default_factory=tuple)
    summary_message: str = ""


def _section_matches_keywords(section_name: str, keywords: frozenset[str]) -> bool:
    """Check if any keyword from the set is a substring of the section name (case-insensitive)."""
    lower = section_name.lower().replace("_", " ")
    for keyword in keywords:
        if keyword in lower:
            return True
    return False


def _value_matches_keywords(
    row_value: str,
    keywords: frozenset[str],
) -> bool:
    """Check if any keyword appears as a token in the row value (case-insensitive)."""
    lower = row_value.lower()
    for keyword in keywords:
        if keyword in lower:
            return True
    return False


def _classify_panel(
    panel: Any,
) -> tuple[str, list[FactoryReadinessReason]]:
    """Scan a single ReviewPanelReadModel and return (max_severity, reasons).

    The max_severity is the highest classification found in this panel.
    It's used to aggregate across panels.
    """
    max_severity = _SEVERITY_INFO
    reasons: list[FactoryReadinessReason] = []

    if not panel.available or panel.stale:
        return _SEVERITY_INFO, reasons

    panel_name = panel.panel_name

    for section in getattr(panel, "sections", ()) or ():
        section_name = getattr(section, "section_name", "") or ""

        # ── Determine section-level severity from section name ──────────
        if _section_matches_keywords(section_name, _BLOCKED_SECTION_KEYWORDS):
            section_severity = _SEVERITY_BLOCKED
        elif _section_matches_keywords(section_name, _ERROR_SECTION_KEYWORDS):
            section_severity = _SEVERITY_ERROR
        elif _section_matches_keywords(section_name, _WARNING_SECTION_KEYWORDS):
            section_severity = _SEVERITY_WARNING
        elif _section_matches_keywords(section_name, _READY_SECTION_KEYWORDS):
            section_severity = _SEVERITY_INFO
        else:
            section_severity = None  # will be determined per-row

        # ── Process each row ────────────────────────────────────────────
        for row in getattr(section, "rows", ()) or ():
            if not row or len(row) < 2:
                continue
            label = row[0]
            value = row[1]
            if not value:
                continue

            # Determine per-row severity by checking value keywords first,
            # falling back to section-level severity
            row_severity = section_severity

            if _value_matches_keywords(value, _BLOCKED_VALUE_KEYWORDS):
                row_severity = _higher_severity(row_severity, _SEVERITY_BLOCKED)
            elif _value_matches_keywords(value, _ERROR_VALUE_KEYWORDS):
                row_severity = _higher_severity(row_severity, _SEVERITY_ERROR)
            elif _value_matches_keywords(value, _WARNING_VALUE_KEYWORDS):
                row_severity = _higher_severity(row_severity, _SEVERITY_WARNING)
            elif _value_matches_keywords(value, _READY_VALUE_KEYWORDS):
                if row_severity is None:
                    row_severity = _SEVERITY_INFO

            if row_severity is None:
                continue

            max_severity = _higher_severity(max_severity, row_severity)
            reasons.append(FactoryReadinessReason(
                reason_text=f"{section_name}: {label} — {value}",
                source_panel=panel_name,
                severity=row_severity,
            ))

        # ── Also check section warnings ────────────────────────────────
        for warning in getattr(section, "warnings", ()) or ():
            if _value_matches_keywords(warning, _BLOCKED_VALUE_KEYWORDS):
                max_severity = _higher_severity(max_severity, _SEVERITY_BLOCKED)
                reasons.append(FactoryReadinessReason(
                    reason_text=warning,
                    source_panel=panel_name,
                    severity=_SEVERITY_BLOCKED,
                ))
            elif _value_matches_keywords(warning, _ERROR_VALUE_KEYWORDS):
                max_severity = _higher_severity(max_severity, _SEVERITY_ERROR)
                reasons.append(FactoryReadinessReason(
                    reason_text=warning,
                    source_panel=panel_name,
                    severity=_SEVERITY_ERROR,
                ))
            elif _value_matches_keywords(warning, _WARNING_VALUE_KEYWORDS):
                max_severity = _higher_severity(max_severity, _SEVERITY_WARNING)
                reasons.append(FactoryReadinessReason(
                    reason_text=warning,
                    source_panel=panel_name,
                    severity=_SEVERITY_WARNING,
                ))

    return max_severity, reasons


def _higher_severity(a: str, b: str) -> str:
    """Return the more severe of two severity strings."""
    if _SEVERITY_PRIORITY.get(b, 0) > _SEVERITY_PRIORITY.get(a, 0):
        return b
    return a


def _severity_to_status(severity: str) -> str:
    """Map the highest severity found to a FactoryReadinessStatus."""
    mapping = {
        _SEVERITY_BLOCKED: BLOCKED,
        _SEVERITY_ERROR: NOT_READY,
        _SEVERITY_WARNING: NEEDS_REVIEW,
    }
    return mapping.get(severity, READY)


def _build_summary(
    status: str,
    has_reasons: bool,
    blocking_count: int,
    warning_count: int,
    ready_count: int,
) -> str:
    """Build a human-readable summary message."""
    if not has_reasons:
        return "No review panel data available for factory readiness assessment."

    parts: list[str] = [f"Factory readiness: {status}"]
    if blocking_count > 0:
        parts.append(f"{blocking_count} blocker(s)")
    if warning_count > 0:
        parts.append(f"{warning_count} warning(s)")
    if ready_count > 0:
        parts.append(f"{ready_count} ready signal(s)")
    return " — ".join(parts)


def build_factory_readiness_read_model(
    review_panels: Any = None,
) -> FactoryReadinessReadModel:
    """Build a FactoryReadinessReadModel from existing review panel data.

    Accepts:
    - A tuple/list of ReviewPanelReadModel instances
    - A single ReviewPanelReadModel
    - None

    The function is deterministic and side-effect free. It scans the
    section names, row values, and warnings of each review panel to
    classify the overall factory readiness status.

    Returns FactoryReadinessReadModel with status, reasons, and counts.
    No domain objects leak into the output.
    """
    if review_panels is None:
        return FactoryReadinessReadModel(
            status=UNKNOWN,
            summary_message=_build_summary(UNKNOWN, False, 0, 0, 0),
        )

    if not isinstance(review_panels, (list, tuple)):
        review_panels = (review_panels,)

    if not review_panels:
        return FactoryReadinessReadModel(
            status=UNKNOWN,
            summary_message=_build_summary(UNKNOWN, False, 0, 0, 0),
        )

    all_reasons: list[FactoryReadinessReason] = []
    max_severity: str = _SEVERITY_INFO
    source_panels_set: set[str] = set()

    for panel in review_panels:
        if panel is None:
            continue
        panel_severity, panel_reasons = _classify_panel(panel)
        max_severity = _higher_severity(max_severity, panel_severity)
        all_reasons.extend(panel_reasons)
        panel_name = getattr(panel, "panel_name", "") or ""
        if panel_name:
            source_panels_set.add(panel_name)

    # Count by severity
    blocking_count = sum(
        1 for r in all_reasons if r.severity == _SEVERITY_BLOCKED
    )
    warning_count = sum(
        1 for r in all_reasons if r.severity == _SEVERITY_WARNING
    )
    ready_count = sum(
        1 for r in all_reasons if r.severity == _SEVERITY_INFO
    )

    # Determine status from highest severity
    has_reasons = len(all_reasons) > 0
    if not has_reasons:
        status = UNKNOWN
    else:
        status = _severity_to_status(max_severity)

    return FactoryReadinessReadModel(
        status=status,
        reasons=tuple(all_reasons),
        blocking_count=blocking_count,
        warning_count=warning_count,
        ready_count=ready_count,
        source_panels=tuple(sorted(source_panels_set)),
        summary_message=_build_summary(status, has_reasons, blocking_count, warning_count, ready_count),
    )


__all__ = [
    "READY",
    "NOT_READY",
    "NEEDS_REVIEW",
    "BLOCKED",
    "UNKNOWN",
    "FactoryReadinessReason",
    "FactoryReadinessReadModel",
    "build_factory_readiness_read_model",
]
