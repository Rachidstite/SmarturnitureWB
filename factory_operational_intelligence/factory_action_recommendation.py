# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Operational Intelligence
# Factory Action Recommendation Read Model
#
# Transforms FactoryBlockingAnalysisReadModel items into
# actionable recommendations by referencing existing domain knowledge.
#
# Follows ADR-FOI-3: recommendations reference existing knowledge,
# never invent knowledge.
#
# This module is:
# - deterministic and side-effect free
# - purely a read model builder
# - no engine, workflow, or service
# - no domain imports
# - no calculations
# - no decisions
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ── Confidence constants ─────────────────────────────────────────────

HIGH = "HIGH"
MEDIUM = "MEDIUM"
LOW = "LOW"
NONE = "NONE"

# ── Knowledge source constants ───────────────────────────────────────

ENGINEERING = "Engineering"
MANUFACTURING = "Manufacturing"
COST = "Cost"
COMMERCIAL = "Commercial"
RELEASE = "Release"
OPERATIONAL_POLICY = "Operational Policy"
UNKNOWN_SOURCE = "Unknown"

# ── Recommendation mapping key: (operational_category, severity) ─────

_KNOWLEDGE_MAP: dict[tuple[str, str], dict[str, str]] = {
    # ── Engineering ───────────────────────────────────────────────────
    ("ENGINEERING", "BLOCKED"): {
        "knowledge_source": ENGINEERING,
        "knowledge_reference": "Engineering tolerance and geometry rules",
        "responsible_domain": "Engineering",
        "recommended_action": "Review design dimensions against engineering tolerance specifications and correct the violating geometry.",
        "recommendation_reason": "Engineering validation rule violation — design must conform to tolerance constraints before production.",
        "confidence": HIGH,
    },
    ("ENGINEERING", "ERROR"): {
        "knowledge_source": ENGINEERING,
        "knowledge_reference": "Engineering tolerance and geometry rules",
        "responsible_domain": "Engineering",
        "recommended_action": "Review design dimensions against engineering tolerance specifications.",
        "recommendation_reason": "Engineering validation rule produced an error — design should be reviewed and corrected.",
        "confidence": HIGH,
    },
    ("ENGINEERING", "WARNING"): {
        "knowledge_source": ENGINEERING,
        "knowledge_reference": "Engineering tolerance and geometry rules",
        "responsible_domain": "Engineering",
        "recommended_action": "Review design dimensions near tolerance limits — consider adjusting or confirming with engineering.",
        "recommendation_reason": "Engineering validation warning — parameter is near the defined tolerance boundary.",
        "confidence": MEDIUM,
    },
    # ── Manufacturing ────────────────────────────────────────────────
    ("MANUFACTURING", "BLOCKED"): {
        "knowledge_source": MANUFACTURING,
        "knowledge_reference": "Manufacturing capability and CNC tables",
        "responsible_domain": "Manufacturing",
        "recommended_action": "Verify manufacturing parameters against CNC capability tables and machine specifications.",
        "recommendation_reason": "Manufacturing operation blocked — CNC or assembly constraint prevents execution with current parameters.",
        "confidence": HIGH,
    },
    ("MANUFACTURING", "ERROR"): {
        "knowledge_source": MANUFACTURING,
        "knowledge_reference": "Manufacturing capability and CNC tables",
        "responsible_domain": "Manufacturing",
        "recommended_action": "Review manufacturing operation against machine capability and adjust parameters or process.",
        "recommendation_reason": "Manufacturing operation failed — check CNC parameters, tooling, and material compatibility.",
        "confidence": HIGH,
    },
    ("MANUFACTURING", "WARNING"): {
        "knowledge_source": MANUFACTURING,
        "knowledge_reference": "Manufacturing capability and CNC tables",
        "responsible_domain": "Manufacturing",
        "recommended_action": "Review manufacturing operation parameters — near capability limits, consider adjustment.",
        "recommendation_reason": "Manufacturing operation warning — parameter is near the defined capability boundary.",
        "confidence": MEDIUM,
    },
    # ── Cost ─────────────────────────────────────────────────────────
    ("COST", "BLOCKED"): {
        "knowledge_source": COST,
        "knowledge_reference": "Cost estimation and budget rules",
        "responsible_domain": "Cost",
        "recommended_action": "Review cost estimate against budget thresholds — cost blocker must be resolved before production.",
        "recommendation_reason": "Cost threshold violated — project cost exceeds approved budget. Requires cost manager review.",
        "confidence": HIGH,
    },
    ("COST", "ERROR"): {
        "knowledge_source": COST,
        "knowledge_reference": "Cost estimation and budget rules",
        "responsible_domain": "Cost",
        "recommended_action": "Review cost estimate against budget and correct the pricing discrepancy.",
        "recommendation_reason": "Cost estimation error — pricing data is incomplete or inconsistent with expected values.",
        "confidence": HIGH,
    },
    ("COST", "WARNING"): {
        "knowledge_source": COST,
        "knowledge_reference": "Cost estimation and budget rules",
        "responsible_domain": "Cost",
        "recommended_action": "Monitor cost against budget — current estimate is near the threshold.",
        "recommendation_reason": "Cost warning — estimated cost is approaching the approved budget limit.",
        "confidence": MEDIUM,
    },
    # ── Commercial ───────────────────────────────────────────────────
    ("COMMERCIAL", "BLOCKED"): {
        "knowledge_source": COMMERCIAL,
        "knowledge_reference": "Commercial pricing policy and quotation rules",
        "responsible_domain": "Commercial",
        "recommended_action": "Review commercial terms and pricing policy — commercial blocker must be resolved before production.",
        "recommendation_reason": "Commercial policy violation — pricing, discount, or quotation condition blocks release.",
        "confidence": HIGH,
    },
    ("COMMERCIAL", "ERROR"): {
        "knowledge_source": COMMERCIAL,
        "knowledge_reference": "Commercial pricing policy and quotation rules",
        "responsible_domain": "Commercial",
        "recommended_action": "Review commercial data against pricing policy and correct the discrepancy.",
        "recommendation_reason": "Commercial data error — pricing or quotation information is incomplete or inconsistent.",
        "confidence": HIGH,
    },
    ("COMMERCIAL", "WARNING"): {
        "knowledge_source": COMMERCIAL,
        "knowledge_reference": "Commercial pricing policy and quotation rules",
        "responsible_domain": "Commercial",
        "recommended_action": "Review commercial terms — pending approval or near policy limits.",
        "recommendation_reason": "Commercial warning — pricing or approval is pending or near defined policy boundaries.",
        "confidence": MEDIUM,
    },
    # ── Release ──────────────────────────────────────────────────────
    ("RELEASE", "BLOCKED"): {
        "knowledge_source": RELEASE,
        "knowledge_reference": "Release readiness criteria and approval rules",
        "responsible_domain": "Release",
        "recommended_action": "Resolve all blocked release checklist items — release cannot proceed until blockers are cleared.",
        "recommendation_reason": "Release blocker — a required checklist item or approval is not satisfied.",
        "confidence": HIGH,
    },
    ("RELEASE", "ERROR"): {
        "knowledge_source": RELEASE,
        "knowledge_reference": "Release readiness criteria and approval rules",
        "responsible_domain": "Release",
        "recommended_action": "Complete pending release checklist items and obtain required approvals.",
        "recommendation_reason": "Release criteria not met — one or more release requirements are incomplete or failed.",
        "confidence": HIGH,
    },
    ("RELEASE", "WARNING"): {
        "knowledge_source": RELEASE,
        "knowledge_reference": "Release readiness criteria and approval rules",
        "responsible_domain": "Release",
        "recommended_action": "Review pending release items — some criteria may need attention before final release.",
        "recommendation_reason": "Release warning — one or more release criteria are approaching deadline or require review.",
        "confidence": MEDIUM,
    },
}


def _lookup_recommendation(
    category: str,
    severity: str,
) -> dict[str, str] | None:
    """Look up recommendation data for a given category and severity.

    Returns None if no mapping exists, indicating no automated recommendation.
    """
    return _KNOWLEDGE_MAP.get((category, severity))


def _build_recommendation(
    blocking_item: Any,
    index: int,
) -> tuple[dict[str, str], str]:
    """Build a single recommendation dict from a blocking item.

    Returns (recommendation_data, recommendation_id).
    recommendation_data contains the resolved fields.
    """
    category = getattr(blocking_item, "operational_category", "") or ""
    severity = getattr(blocking_item, "severity", "") or ""
    source_panel = getattr(blocking_item, "source_panel", "") or ""

    rid = f"REC-{index + 1:04d}"

    mapping = _lookup_recommendation(category, severity)

    if mapping is None:
        # No automated recommendation available
        return {
            "recommendation_id": rid,
            "blocking_reference": category,
            "knowledge_source": UNKNOWN_SOURCE,
            "knowledge_reference": "",
            "responsible_domain": source_panel or "Unknown",
            "recommended_action": "No automated recommendation available — requires manual review by the responsible domain.",
            "recommendation_reason": "",
            "confidence": NONE,
            "human_message": f"No automated recommendation for {severity.lower()} issue in {category.lower()}.",
            "optional_notes": "",
        }, rid

    human_message = (
        f"[{mapping['confidence']}] {mapping['recommended_action']} "
        f"({mapping['knowledge_source']} — {mapping['knowledge_reference']})"
    )

    return {
        "recommendation_id": rid,
        "blocking_reference": category,
        "knowledge_source": mapping["knowledge_source"],
        "knowledge_reference": mapping["knowledge_reference"],
        "responsible_domain": mapping["responsible_domain"],
        "recommended_action": mapping["recommended_action"],
        "recommendation_reason": mapping["recommendation_reason"],
        "confidence": mapping["confidence"],
        "human_message": human_message,
        "optional_notes": "",
    }, rid


def _build_summary(
    status: str,
    high_count: int,
    medium_count: int,
    low_count: int,
    none_count: int,
) -> str:
    """Build a human-readable summary of the recommendation analysis."""
    parts: list[str] = [f"Factory action recommendations: {status}"]
    if high_count > 0:
        parts.append(f"{high_count} high confidence")
    if medium_count > 0:
        parts.append(f"{medium_count} medium confidence")
    if low_count > 0:
        parts.append(f"{low_count} low confidence")
    if none_count > 0:
        parts.append(f"{none_count} no recommendation")
    return " — ".join(parts)


@dataclass(frozen=True)
class FactoryRecommendation:
    """A single actionable recommendation following ADR-FOI-3.

    Attributes:
        recommendation_id: Unique identifier for traceability (e.g. REC-0001).
        blocking_reference: The operational category this recommendation addresses.
        knowledge_source: The knowledge domain that provides this recommendation.
        knowledge_reference: Specific knowledge artifact referenced.
        responsible_domain: The domain that owns the referenced knowledge.
        recommended_action: What action is recommended.
        recommendation_reason: Why this action is recommended.
        confidence: HIGH, MEDIUM, LOW, or NONE.
        human_message: Human-readable recommendation summary.
        optional_notes: Additional context (may be empty).
    """

    recommendation_id: str = ""
    blocking_reference: str = ""
    knowledge_source: str = ""
    knowledge_reference: str = ""
    responsible_domain: str = ""
    recommended_action: str = ""
    recommendation_reason: str = ""
    confidence: str = NONE
    human_message: str = ""
    optional_notes: str = ""


@dataclass(frozen=True)
class FactoryRecommendationReadModel:
    """Read-only collection of actionable recommendations.

    Attributes:
        status: Mirror of the input blocking analysis status.
        recommendations: All recommendations derived from blocking items.
        high_confidence_count: Number of HIGH confidence recommendations.
        medium_confidence_count: Number of MEDIUM confidence recommendations.
        low_confidence_count: Number of LOW confidence recommendations.
        none_confidence_count: Number of NONE confidence (no recommendation) items.
        summary_message: Human-readable one-line summary.
    """

    status: str = ""
    recommendations: tuple[FactoryRecommendation, ...] = field(default_factory=tuple)
    high_confidence_count: int = 0
    medium_confidence_count: int = 0
    low_confidence_count: int = 0
    none_confidence_count: int = 0
    summary_message: str = ""


def build_factory_action_recommendation_read_model(
    blocking_analysis: Any = None,
) -> FactoryRecommendationReadModel:
    """Build a FactoryRecommendationReadModel from blocking analysis.

    Accepts:
    - blocking_analysis: A FactoryBlockingAnalysisReadModel (or None)

    Maps each FactoryBlockingItem to a FactoryRecommendation using a
    deterministic knowledge lookup table per ADR-FOI-3.

    The function is deterministic and side-effect free. It never:
    - calculates geometry, machining, cost, or quotation
    - invents missing engineering rules
    - generates AI guesses
    - makes production decisions
    """
    if blocking_analysis is None:
        return FactoryRecommendationReadModel(
            status="",
            summary_message=_build_summary("", 0, 0, 0, 0),
        )

    status = getattr(blocking_analysis, "status", "") or ""
    blocking_items = getattr(blocking_analysis, "blocking_items", ()) or ()

    recommendations: list[FactoryRecommendation] = []
    high_count = 0
    medium_count = 0
    low_count = 0
    none_count = 0

    for index, item in enumerate(blocking_items):
        rec_data, rid = _build_recommendation(item, index)

        rec = FactoryRecommendation(
            recommendation_id=rec_data["recommendation_id"],
            blocking_reference=rec_data["blocking_reference"],
            knowledge_source=rec_data["knowledge_source"],
            knowledge_reference=rec_data["knowledge_reference"],
            responsible_domain=rec_data["responsible_domain"],
            recommended_action=rec_data["recommended_action"],
            recommendation_reason=rec_data["recommendation_reason"],
            confidence=rec_data["confidence"],
            human_message=rec_data["human_message"],
            optional_notes=rec_data["optional_notes"],
        )
        recommendations.append(rec)

        if rec.confidence == HIGH:
            high_count += 1
        elif rec.confidence == MEDIUM:
            medium_count += 1
        elif rec.confidence == LOW:
            low_count += 1
        else:
            none_count += 1

    return FactoryRecommendationReadModel(
        status=status,
        recommendations=tuple(recommendations),
        high_confidence_count=high_count,
        medium_confidence_count=medium_count,
        low_confidence_count=low_count,
        none_confidence_count=none_count,
        summary_message=_build_summary(status, high_count, medium_count, low_count, none_count),
    )


__all__ = [
    "HIGH",
    "MEDIUM",
    "LOW",
    "NONE",
    "FactoryRecommendation",
    "FactoryRecommendationReadModel",
    "build_factory_action_recommendation_read_model",
]
