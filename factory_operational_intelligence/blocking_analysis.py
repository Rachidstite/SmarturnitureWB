# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Operational Intelligence
# Factory Blocking Analysis Read Model
#
# Translates FactoryReadinessReason entries into structured
# OperationalBlockingItem objects following ADR-FOI-2.
#
# Provides diagnosis only — no recommendations, no decisions.
#
# This module is:
# - deterministic and side-effect free
# - purely a read model builder
# - consumes only FactoryReadinessReadModel + ReviewPanelReadModel
# - no engine, workflow, or service
# - no domain imports
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ── Severity constants (reused from factory_readiness) ───────────────

_SEVERITY_BLOCKED = "BLOCKED"
_SEVERITY_ERROR = "ERROR"
_SEVERITY_WARNING = "WARNING"
_SEVERITY_INFO = "INFO"

# ── Operational category mapping (panel_name → category) ─────────────

_PANEL_CATEGORY: dict[str, str] = {
    "Validation": "ENGINEERING",
    "Manufacturing": "MANUFACTURING",
    "Cost": "COST",
    "Commercial": "COMMERCIAL",
    "Release": "RELEASE",
}

# ── Impact templates per severity ────────────────────────────────────

_IMPACT_TEMPLATES: dict[str, str] = {
    _SEVERITY_BLOCKED: "Blocks production — {panel} issue requires resolution before proceeding.",
    _SEVERITY_ERROR: "Delays production — {panel} issue requires correction before proceeding.",
    _SEVERITY_WARNING: "May affect production — {panel} issue should be reviewed before proceeding.",
    _SEVERITY_INFO: "Information from {panel} — no direct production impact.",
}


@dataclass(frozen=True)
class FactoryBlockingItem:
    """A structured blocking or warning item following ADR-FOI-2.

    Attributes:
        blocking_item_id: Stable deterministic identifier (<PANEL>:<CATEGORY>:<index>).
        operational_category: One of the approved FOI categories (ENGINEERING, MANUFACTURING, etc.)
        source_panel: The ReviewPanelReadModel panel_name that produced this item.
        severity: BLOCKED, ERROR, WARNING, or INFO.
        human_message: Human-readable description answering what/why/impact/who.
        operational_impact: Human-readable description of factory impact.
        technical_detail: Optional technical detail (may be empty).
        component_id: Optional component reference (may be empty).
    """

    blocking_item_id: str = ""
    operational_category: str = ""
    source_panel: str = ""
    severity: str = _SEVERITY_INFO
    human_message: str = ""
    operational_impact: str = ""
    technical_detail: str = ""
    component_id: str = ""


@dataclass(frozen=True)
class FactoryBlockingAnalysisReadModel:
    """Read-only analysis of factory blocking items.

    Attributes:
        status: Mirror of the input FactoryReadiness status.
        blocking_items: All blocking/diagnostic items with operational language.
        critical_count: Number of BLOCKED-severity items.
        high_count: Number of ERROR-severity items.
        medium_count: Number of WARNING-severity items.
        low_count: Number of INFO-severity items.
        summary_message: Human-readable one-line summary.
        source_panels: Panels that contributed data to this analysis.
    """

    status: str = ""
    blocking_items: tuple[FactoryBlockingItem, ...] = field(default_factory=tuple)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    summary_message: str = ""
    source_panels: tuple[str, ...] = field(default_factory=tuple)


def _map_category(panel_name: str) -> str:
    """Map a ReviewPanelReadModel panel_name to an operational category.

    Falls back to UNKNOWN if the panel is not in the known mapping.
    """
    return _PANEL_CATEGORY.get(panel_name, "UNKNOWN")


def _build_impact(severity: str, panel_name: str) -> str:
    """Build an operational impact string from severity and panel name."""
    template = _IMPACT_TEMPLATES.get(severity, _IMPACT_TEMPLATES[_SEVERITY_INFO])
    return template.format(panel=panel_name)


def _build_blocking_item(
    reason: Any,
    index: int,
) -> FactoryBlockingItem:
    """Convert a single FactoryReadinessReason into a FactoryBlockingItem.

    The reason_text from FactoryReadinessReason is used as the human_message.
    The operational_category is derived from the source_panel.
    The operational_impact is built from severity + panel_name.
    The blocking_item_id is deterministic: <panel>:<category>:<index>.
    The technical_detail is empty unless the reason carries extra info — we
    never invent technical details.
    """
    panel_name = getattr(reason, "source_panel", "") or ""
    severity = getattr(reason, "severity", _SEVERITY_INFO) or _SEVERITY_INFO
    reason_text = getattr(reason, "reason_text", "") or ""
    category = _map_category(panel_name)

    # Deterministic ID: Normalize panel and category, append index
    panel_norm = panel_name.upper().replace(" ", "_")
    cat_norm = category.upper().replace(" ", "_")
    blocking_item_id = f"{panel_norm}:{cat_norm}:{index}"

    return FactoryBlockingItem(
        blocking_item_id=blocking_item_id,
        operational_category=category,
        source_panel=panel_name,
        severity=severity,
        human_message=reason_text,
        operational_impact=_build_impact(severity, panel_name),
        technical_detail="",
        component_id="",
    )


def _build_summary(
    status: str,
    critical: int,
    high: int,
    medium: int,
    low: int,
) -> str:
    """Build a human-readable summary of the blocking analysis."""
    parts: list[str] = [f"Factory blocking analysis: {status}"]
    if critical > 0:
        parts.append(f"{critical} critical")
    if high > 0:
        parts.append(f"{high} high")
    if medium > 0:
        parts.append(f"{medium} medium")
    if low > 0:
        parts.append(f"{low} low")
    return " — ".join(parts)


def build_factory_blocking_analysis_read_model(
    readiness: Any = None,
    review_panels: Any = None,
) -> FactoryBlockingAnalysisReadModel:
    """Build a FactoryBlockingAnalysisReadModel from readiness + review panels.

    Accepts:
    - readiness: A FactoryReadinessReadModel (or None)
    - review_panels: A tuple/list of ReviewPanelReadModel (or None)

    Processes FactoryReadinessReason entries into FactoryBlockingItem objects
    with operational language per ADR-FOI-2.

    The function is deterministic and side-effect free. It projects existing
    facts — it does not calculate, recommend, or decide.
    """
    if readiness is None:
        return FactoryBlockingAnalysisReadModel(
            status="",
            summary_message=_build_summary("", 0, 0, 0, 0),
        )

    status = getattr(readiness, "status", "") or ""
    reasons = getattr(readiness, "reasons", ()) or ()
    readiness_source_panels = getattr(readiness, "source_panels", ()) or ()

    # If no reasons and no panels, return empty analysis
    if not reasons and not readiness_source_panels:
        return FactoryBlockingAnalysisReadModel(
            status=status,
            summary_message=_build_summary(status, 0, 0, 0, 0),
        )

    # Build blocking items from readiness reasons
    blocking_items: list[FactoryBlockingItem] = []
    source_panels_set: set[str] = set(readiness_source_panels)

    for index, reason in enumerate(reasons):
        item = _build_blocking_item(reason, index)
        blocking_items.append(item)
        if item.source_panel:
            source_panels_set.add(item.source_panel)

    # Count by severity
    critical_count = sum(1 for b in blocking_items if b.severity == _SEVERITY_BLOCKED)
    high_count = sum(1 for b in blocking_items if b.severity == _SEVERITY_ERROR)
    medium_count = sum(1 for b in blocking_items if b.severity == _SEVERITY_WARNING)
    low_count = sum(1 for b in blocking_items if b.severity == _SEVERITY_INFO)

    return FactoryBlockingAnalysisReadModel(
        status=status,
        blocking_items=tuple(blocking_items),
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        summary_message=_build_summary(status, critical_count, high_count, medium_count, low_count),
        source_panels=tuple(sorted(source_panels_set)),
    )


__all__ = [
    "FactoryBlockingItem",
    "FactoryBlockingAnalysisReadModel",
    "build_factory_blocking_analysis_read_model",
]
