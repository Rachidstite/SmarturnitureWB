# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Dashboard
# Dashboard Read Model
#
# Aggregates existing FOI read models into a single operational
# snapshot for factory supervisors.
#
# This module is:
# - deterministic and side-effect free
# - purely a read model builder — no engine, workflow, or service
# - consumes only FOI read models — no domain imports
# - never duplicates FOI business logic
# - never calculates readiness, blocking, recommendations, or decisions
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FactoryDashboardSection:
    """A single section within the factory dashboard.

    Each section wraps one FOI layer (Readiness, Blocking Analysis,
    Action Recommendations, or Production Decision) as key-value rows.

    Attributes:
        section_name: Human-readable section name.
        rows: Key-value pairs from the FOI read model fields.
    """

    section_name: str = ""
    rows: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class FactoryDashboardReadModel:
    """Consolidated operational snapshot of factory readiness.

    Aggregates existing FOI outputs into one read model.
    Every field is copied from a pre-computed FOI read model —
    never derived or computed here.

    Attributes:
        sections: Dashboard sections for each available FOI layer.
        factory_status: Mirror of FactoryReadinessReadModel.status.
        decision_status: Mirror of ProductionDecisionReadModel.decision_status.
        critical_blocker_count: Mirror of FactoryBlockingAnalysisReadModel.critical_count.
        recommendation_count: Number of recommendations (from len of recommendations tuple).
        summary_message: Mirror of ProductionDecisionReadModel.summary_message.
        available: True when at least one FOI read model was provided.
    """

    sections: tuple[FactoryDashboardSection, ...] = field(default_factory=tuple)
    factory_status: str = ""
    decision_status: str = ""
    critical_blocker_count: int = 0
    recommendation_count: int = 0
    summary_message: str = ""
    available: bool = False


# ── Section builders (private helpers) ────────────────────────────────


def _build_readiness_section(readiness: Any) -> FactoryDashboardSection | None:
    """Build a dashboard section from FactoryReadinessReadModel.

    Reads pre-computed fields only — no status determination.
    """
    if readiness is None:
        return None
    status = getattr(readiness, "status", "") or ""
    if not status:
        return None
    blocking = getattr(readiness, "blocking_count", 0) or 0
    warnings = getattr(readiness, "warning_count", 0) or 0
    ready = getattr(readiness, "ready_count", 0) or 0
    summary = getattr(readiness, "summary_message", "") or ""
    rows: list[tuple[str, str]] = [
        ("Status", status),
        ("Blockers", str(blocking)),
        ("Warnings", str(warnings)),
        ("Ready Signals", str(ready)),
    ]
    if summary:
        rows.append(("Summary", summary))
    return FactoryDashboardSection(
        section_name="Factory Readiness",
        rows=tuple(rows),
    )


def _build_blocking_section(blocking: Any) -> FactoryDashboardSection | None:
    """Build a dashboard section from FactoryBlockingAnalysisReadModel.

    Reads pre-computed counts — no severity classification.
    """
    if blocking is None:
        return None
    status = getattr(blocking, "status", "") or ""
    critical = getattr(blocking, "critical_count", 0) or 0
    high = getattr(blocking, "high_count", 0) or 0
    medium = getattr(blocking, "medium_count", 0) or 0
    low = getattr(blocking, "low_count", 0) or 0
    summary = getattr(blocking, "summary_message", "") or ""
    rows: list[tuple[str, str]] = [
        ("Status", status),
    ]
    if critical > 0:
        rows.append(("Critical Blockers", str(critical)))
    if high > 0:
        rows.append(("Errors", str(high)))
    if medium > 0:
        rows.append(("Warnings", str(medium)))
    if low > 0:
        rows.append(("Info Items", str(low)))
    if summary:
        rows.append(("Summary", summary))
    return FactoryDashboardSection(
        section_name="Blocking Analysis",
        rows=tuple(rows),
    )


def _build_recommendation_section(
    recommendations: Any,
) -> FactoryDashboardSection | None:
    """Build a dashboard section from FactoryRecommendationReadModel.

    Reads pre-computed counts — no confidence derivation.
    """
    if recommendations is None:
        return None
    recs = getattr(recommendations, "recommendations", ()) or ()
    if not recs:
        return None
    high = getattr(recommendations, "high_confidence_count", 0) or 0
    medium = getattr(recommendations, "medium_confidence_count", 0) or 0
    low = getattr(recommendations, "low_confidence_count", 0) or 0
    none_c = getattr(recommendations, "none_confidence_count", 0) or 0
    summary = getattr(recommendations, "summary_message", "") or ""
    rows: list[tuple[str, str]] = [
        ("Available", str(len(recs))),
    ]
    if high > 0:
        rows.append(("High Confidence", str(high)))
    if medium > 0:
        rows.append(("Medium Confidence", str(medium)))
    if low > 0:
        rows.append(("Low Confidence", str(low)))
    if none_c > 0:
        rows.append(("No Recommendation", str(none_c)))
    if summary:
        rows.append(("Summary", summary))
    return FactoryDashboardSection(
        section_name="Action Recommendations",
        rows=tuple(rows),
    )


def _build_decision_section(decision: Any) -> FactoryDashboardSection | None:
    """Build a dashboard section from ProductionDecisionReadModel.

    Reads pre-computed fields — no decision logic.
    """
    if decision is None:
        return None
    status = getattr(decision, "decision_status", "") or ""
    if not status:
        return None
    confidence = getattr(decision, "confidence", "") or ""
    summary = getattr(decision, "summary_message", "") or ""
    blocking_ids = getattr(decision, "blocking_item_ids", ()) or ()
    rec_ids = getattr(decision, "recommendation_ids", ()) or ()
    rows: list[tuple[str, str]] = [
        ("Production Decision", status),
        ("Confidence", confidence),
    ]
    if blocking_ids:
        rows.append(("Referenced Blockers", str(len(blocking_ids))))
    if rec_ids:
        rows.append(("Referenced Recommendations", str(len(rec_ids))))
    if summary:
        rows.append(("Summary", summary))
    return FactoryDashboardSection(
        section_name="Production Decision",
        rows=tuple(rows),
    )


# ── Public builder ────────────────────────────────────────────────────


def build_factory_dashboard_read_model(
    readiness: Any = None,
    blocking: Any = None,
    recommendations: Any = None,
    decision: Any = None,
) -> FactoryDashboardReadModel:
    """Build a consolidated dashboard read model from FOI outputs.

    Accepts:
        readiness: A FactoryReadinessReadModel (or None).
        blocking: A FactoryBlockingAnalysisReadModel (or None).
        recommendations: A FactoryRecommendationReadModel (or None).
        decision: A ProductionDecisionReadModel (or None).

    Returns a frozen FactoryDashboardReadModel with sections for each
    available FOI layer and a summary copied from the decision model.

    No FOI business logic is duplicated — fields are only read via
    getattr() from pre-computed FOI outputs.
    """
    sections: list[FactoryDashboardSection] = []

    readiness_section = _build_readiness_section(readiness)
    if readiness_section is not None:
        sections.append(readiness_section)

    blocking_section = _build_blocking_section(blocking)
    if blocking_section is not None:
        sections.append(blocking_section)

    rec_section = _build_recommendation_section(recommendations)
    if rec_section is not None:
        sections.append(rec_section)

    decision_section = _build_decision_section(decision)
    if decision_section is not None:
        sections.append(decision_section)

    # ── Summary fields — copied from pre-computed FOI outputs only ──
    factory_status = getattr(readiness, "status", "") or ""
    decision_status = getattr(decision, "decision_status", "") or ""
    critical_blocker_count = getattr(blocking, "critical_count", 0) or 0
    recs_tuple = getattr(recommendations, "recommendations", ()) or ()
    recommendation_count = len(recs_tuple)
    summary_message = getattr(decision, "summary_message", "") or ""

    return FactoryDashboardReadModel(
        sections=tuple(sections),
        factory_status=factory_status,
        decision_status=decision_status,
        critical_blocker_count=critical_blocker_count,
        recommendation_count=recommendation_count,
        summary_message=summary_message,
        available=len(sections) > 0,
    )


# ── Manufacturing Render Review section ──────────────────────────────


def build_manufacturing_render_dashboard_section(
    commands: Any = None,
) -> FactoryDashboardSection | None:
    """Build a dashboard section from SceneRenderer viewport commands.

    Accepts an iterable of viewport command dicts (or a single dict)
    and scans for the rendering-only metadata fields that SceneRenderer
    derives from overlay data:

      review_priority, review_category, hole_style,
      drill_direction, hole_depth, hole_depth_mode

    Returns a ``FactoryDashboardSection`` with one row per distinct
    metadata field found, or ``None`` when no commands or no known
    fields are present.

    This is a pure consumption of existing renderer output:
    - No values are recomputed from overlay_type, face, depth, or
      is_through.
    - No manufacturing logic, no cost logic, no feasibility logic.
    - No duplicate extraction logic — only getattr/read from the
      command dicts that SceneRenderer already populated.
    """
    if commands is None:
        return None

    if isinstance(commands, dict):
        commands = [commands]

    _KNOWN_FIELDS = frozenset({
        "review_priority",
        "review_category",
        "hole_style",
        "drill_direction",
        "hole_depth",
        "hole_depth_mode",
    })

    collected: dict[str, set[str]] = {k: set() for k in _KNOWN_FIELDS}

    for cmd in commands or ():
        if not isinstance(cmd, dict):
            continue
        for field in _KNOWN_FIELDS:
            raw = cmd.get(field)
            if raw is not None:
                collected[field].add(str(raw))

    rows: list[tuple[str, str]] = []
    for field in (
        "review_priority",
        "review_category",
        "hole_style",
        "drill_direction",
        "hole_depth",
        "hole_depth_mode",
    ):
        values = collected.get(field, set())
        if not values:
            continue
        label = field.replace("_", " ").title()
        value = ", ".join(sorted(values, key=str))
        rows.append((label, value))

    if not rows:
        return None

    return FactoryDashboardSection(
        section_name="Manufacturing Review Details",
        rows=tuple(rows),
    )


__all__ = [
    "FactoryDashboardSection",
    "FactoryDashboardReadModel",
    "build_factory_dashboard_read_model",
    "build_manufacturing_render_dashboard_section",
]
