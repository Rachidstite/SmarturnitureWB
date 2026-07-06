# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Dashboard
# Manufacturing Review Summary
#
# Lightweight summary of manufacturing review items from existing
# renderer viewport command metadata.
#
# This module is:
# - deterministic and side-effect free
# - purely a read model builder — no engine, workflow, or service
# - consumes only viewport command dict fields — no domain imports
# - never duplicates SceneRenderer derivation logic
# - never computes feasibility, costs, or factory readiness
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ManufacturingReviewSummary:
    """Lightweight summary of manufacturing review rendering metadata.

    Counts are derived only by reading pre-computed fields from
    viewport command dicts — no derivation, no recomputation.

    Attributes:
        total_review_items: Number of viewport commands with review metadata.
        high_priority_count: Commands with review_priority == "high".
        medium_priority_count: Commands with review_priority == "medium".
        low_priority_count: Commands with review_priority == "low".
        drilling_count: Commands with review_category == "drilling".
        hardware_count: Commands with review_category == "hardware".
        edge_banding_count: Commands with review_category == "edge_banding".
        groove_count: Commands with review_category == "groove".
        top_priority_items: Subset of items with the highest priority,
            as ``(panel_identity or source_reference or label, priority)``
            tuples.  Sorted by priority descending.
    """

    total_review_items: int = 0
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    drilling_count: int = 0
    hardware_count: int = 0
    edge_banding_count: int = 0
    groove_count: int = 0
    top_priority_items: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    attention_level: str = "none"
    attention_message: str = ""
    dominant_review_category: str = "none"
    dominant_priority_level: str = "none"
    has_high_priority_items: bool = False
    has_drilling_focus: bool = False


# ── Helpers ──────────────────────────────────────────────────────────


def _resolve_attention_signal(
    total_review_items: int,
    high_priority_count: int,
    medium_priority_count: int,
) -> tuple[str, str]:
    """Determine attention level and message from summary counts.

    Returns a ``(attention_level, attention_message)`` pair where
    ``attention_level`` is one of:

        * ``\"none\"```   — no review items present
        * ``\"urgent\"```  — at least one high-priority item
        * ``\"review\"```  — medium-priority or low-priority items only

    This is a pure function of counts already computed by the caller.
    No derivation from raw command fields, no manufacturing logic,
    no production decision computation.
    """
    if total_review_items <= 0:
        return ("none", "No manufacturing review items.")

    if high_priority_count > 0:
        msg = (
            f"{high_priority_count} high-priority manufacturing review "
            f"item(s) need attention."
        )
        return ("urgent", msg)

    if medium_priority_count > 0:
        msg = (
            f"{medium_priority_count} medium-priority manufacturing review "
            f"item(s) should be reviewed."
        )
        return ("review", msg)

    msg = (
        f"{total_review_items} manufacturing review item(s) available."
    )
    return ("review", msg)


def _resolve_dominant_review_category(
    drilling_count: int,
    hardware_count: int,
    edge_banding_count: int,
    groove_count: int,
) -> str:
    """Determine the review category with the highest item count.

    Returns one of: drilling, hardware, edge_banding, groove, none.

    Tie-break order (highest priority first):
      drilling > hardware > edge_banding > groove

    This is a pure function of counts already computed — no raw
    overlay_type derivation, no manufacturing logic.
    """
    counts: list[tuple[str, int]] = [
        ("drilling", drilling_count),
        ("hardware", hardware_count),
        ("edge_banding", edge_banding_count),
        ("groove", groove_count),
    ]
    # Filter out zeros; tie-break is by declaration order (already correct)
    active = [(cat, cnt) for cat, cnt in counts if cnt > 0]
    if not active:
        return "none"
    # Sort descending by count, then by declaration order (stable sort)
    active.sort(key=lambda x: x[1], reverse=True)
    return active[0][0]


def _resolve_dominant_priority_level(
    high_priority_count: int,
    medium_priority_count: int,
    low_priority_count: int,
) -> str:
    """Determine the priority level with the highest item count.

    Returns one of: high, medium, low, none.

    Tie-break order (highest priority first):
      high > medium > low

    This is a pure function of counts already computed — no
    review_priority field re-read, no derivation logic.
    """
    counts: list[tuple[str, int]] = [
        ("high", high_priority_count),
        ("medium", medium_priority_count),
        ("low", low_priority_count),
    ]
    active = [(level, cnt) for level, cnt in counts if cnt > 0]
    if not active:
        return "none"
    active.sort(key=lambda x: x[1], reverse=True)
    return active[0][0]


def _item_label(cmd: dict[str, Any]) -> str:
    """Best-effort display label for a viewport command."""
    label = cmd.get("label", "")
    if not label:
        label = cmd.get("panel_identity", "")
    if not label:
        label = cmd.get("source_reference", "")
    if not label:
        label = cmd.get("overlay_type", "unknown")
    return str(label)


# ── Public builder ───────────────────────────────────────────────────


def build_manufacturing_review_summary(
    commands: Any = None,
) -> ManufacturingReviewSummary:
    """Build a ManufacturingReviewSummary from viewport command dicts.

    Accepts an iterable of viewport command dicts (SceneRenderer output)
    or a single command dict.  Reads the pre-computed fields
    ``review_priority`` and ``review_category`` directly — never
    re-derives them from ``overlay_type``, ``face``, ``depth``, or
    ``is_through``.

    When *commands* is None or empty, returns a safe zero-summary.
    """
    if commands is None:
        return ManufacturingReviewSummary(
            attention_level="none",
            attention_message="No manufacturing review items.",
        )

    if isinstance(commands, dict):
        commands = [commands]

    # ── Scan each command ───────────────────────────────────────────
    total = 0
    high = 0
    medium = 0
    low = 0
    drilling = 0
    hardware = 0
    edge_banding = 0
    groove = 0
    high_priority_items: list[tuple[str, str]] = []
    medium_priority_items: list[tuple[str, str]] = []
    low_priority_items: list[tuple[str, str]] = []

    for cmd in commands or ():
        if not isinstance(cmd, dict):
            continue

        priority = cmd.get("review_priority", "")
        category = cmd.get("review_category", "")

        # Skip commands without any review metadata
        if not priority and not category:
            continue

        total += 1

        # Priority counts (read directly from review_priority field)
        if priority == "high":
            high += 1
            label = _item_label(cmd)
            high_priority_items.append((label, "high"))
        elif priority == "medium":
            medium += 1
            label = _item_label(cmd)
            medium_priority_items.append((label, "medium"))
        elif priority == "low":
            low += 1
            label = _item_label(cmd)
            low_priority_items.append((label, "low"))

        # Category counts (read directly from review_category field)
        if category == "drilling":
            drilling += 1
        elif category == "hardware":
            hardware += 1
        elif category == "edge_banding":
            edge_banding += 1
        elif category == "groove":
            groove += 1
        # unknown / absent review_category → no category count incremented

    # ── Build top_priority_items (sorted by priority descending) ──────
    top_items: list[tuple[str, str]] = []
    top_items.extend(sorted(high_priority_items, key=lambda x: x[0]))
    top_items.extend(sorted(medium_priority_items, key=lambda x: x[0]))
    top_items.extend(sorted(low_priority_items, key=lambda x: x[0]))

    attention_level, attention_message = _resolve_attention_signal(
        total, high, medium,
    )

    dominant_category = _resolve_dominant_review_category(
        drilling, hardware, edge_banding, groove,
    )
    dominant_priority = _resolve_dominant_priority_level(
        high, medium, low,
    )

    return ManufacturingReviewSummary(
        total_review_items=total,
        high_priority_count=high,
        medium_priority_count=medium,
        low_priority_count=low,
        drilling_count=drilling,
        hardware_count=hardware,
        edge_banding_count=edge_banding,
        groove_count=groove,
        top_priority_items=tuple(top_items),
        attention_level=attention_level,
        attention_message=attention_message,
        dominant_review_category=dominant_category,
        dominant_priority_level=dominant_priority,
        has_high_priority_items=high > 0,
        has_drilling_focus=dominant_category == "drilling",
    )


__all__ = [
    "ManufacturingReviewSummary",
    "build_manufacturing_review_summary",
]
