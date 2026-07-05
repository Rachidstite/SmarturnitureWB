# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Factory Operational Intelligence Presentation Adapter
#
# Converts FOI read models into CV2-native ReviewPanelReadModel data
# for display in the Configurator V2 workspace.
#
# This is a presentation-only adapter. It never:
# - runs FOI analysis (FOI runs independently)
# - duplicates business logic
# - imports from domain modules
# - calculates readiness, blocking, recommendations, or decisions
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from typing import Any

from .read_models import ReviewPanelReadModel, ReviewSectionReadModel


def _build_readiness_section(readiness: Any) -> ReviewSectionReadModel | None:
    """Build a ReviewSectionReadModel from FactoryReadinessReadModel."""
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
    return ReviewSectionReadModel(
        section_name="Factory Readiness",
        rows=tuple(rows),
        warnings=(summary,) if summary else (),
    )


def _build_blocking_section(blocking: Any) -> ReviewSectionReadModel | None:
    """Build a ReviewSectionReadModel from FactoryBlockingAnalysisReadModel."""
    if blocking is None:
        return None
    items = getattr(blocking, "blocking_items", ()) or ()
    if not items:
        return None
    critical = getattr(blocking, "critical_count", 0) or 0
    high = getattr(blocking, "high_count", 0) or 0
    medium = getattr(blocking, "medium_count", 0) or 0
    rows: list[tuple[str, str]] = []
    if critical > 0:
        rows.append(("Critical Blockers", str(critical)))
    if high > 0:
        rows.append(("Errors", str(high)))
    if medium > 0:
        rows.append(("Warnings", str(medium)))
    rows.append(("Total Blocking Items", str(len(items))))
    return ReviewSectionReadModel(
        section_name="Blocking Analysis",
        rows=tuple(rows),
    )


def _build_recommendation_section(recommendations: Any) -> ReviewSectionReadModel | None:
    """Build a ReviewSectionReadModel from FactoryRecommendationReadModel."""
    if recommendations is None:
        return None
    recs = getattr(recommendations, "recommendations", ()) or ()
    if not recs:
        return None
    high = getattr(recommendations, "high_confidence_count", 0) or 0
    medium = getattr(recommendations, "medium_confidence_count", 0) or 0
    low = getattr(recommendations, "low_confidence_count", 0) or 0
    none_c = getattr(recommendations, "none_confidence_count", 0) or 0
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
    return ReviewSectionReadModel(
        section_name="Action Recommendations",
        rows=tuple(rows),
    )


def _build_decision_section(decision: Any) -> ReviewSectionReadModel | None:
    """Build a ReviewSectionReadModel from ProductionDecisionReadModel."""
    if decision is None:
        return None
    status = getattr(decision, "decision_status", "") or ""
    if not status:
        return None
    confidence = getattr(decision, "confidence", "") or ""
    summary = getattr(decision, "summary_message", "") or ""
    rows: list[tuple[str, str]] = [
        ("Production Decision", status),
        ("Confidence", confidence),
    ]
    return ReviewSectionReadModel(
        section_name="Production Decision",
        rows=tuple(rows),
        warnings=(summary,) if summary else (),
    )


def build_foi_presentation_read_model(
    readiness: Any = None,
    blocking: Any = None,
    recommendations: Any = None,
    decision: Any = None,
) -> ReviewPanelReadModel:
    """Build a CV2 ReviewPanelReadModel from FOI read models.

    Accepts:
    - readiness: A FactoryReadinessReadModel (or None)
    - blocking: A FactoryBlockingAnalysisReadModel (or None)
    - recommendations: A FactoryRecommendationReadModel (or None)
    - decision: A ProductionDecisionReadModel (or None)

    Produces a ReviewPanelReadModel(panel_name="Factory Operations")
    with sections for each available FOI layer.

    No FOI business logic is duplicated — this adapter only reads
    already-computed FOI outputs and maps them to CV2 read models.
    """
    sections: list[ReviewSectionReadModel] = []

    decision_section = _build_decision_section(decision)
    if decision_section is not None:
        sections.append(decision_section)

    readiness_section = _build_readiness_section(readiness)
    if readiness_section is not None:
        sections.append(readiness_section)

    blocking_section = _build_blocking_section(blocking)
    if blocking_section is not None:
        sections.append(blocking_section)

    rec_section = _build_recommendation_section(recommendations)
    if rec_section is not None:
        sections.append(rec_section)

    return ReviewPanelReadModel(
        panel_name="Factory Operations",
        sections=tuple(sections),
        available=len(sections) > 0,
    )


__all__ = [
    "build_foi_presentation_read_model",
]
