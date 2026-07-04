# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Presentation Synchronization Contract
#
# Keeps presentation state, binding, and visual contract outputs
# consistent across component ids.
#
# This is a deterministic, side-effect free convenience layer that
# reuses:
#   - FurniturePresentationState
#   - PresentationStateResolver
#   - PresentationVisualContract
#   - resolve_visual_contract
#
# It does NOT create:
#   - StateEngine
#   - PresentationEngine
#   - EventBus
#   - Dispatcher
#   - Store
#   - Reducer
#   - Renderer
#   - Workflow
#
# No domain, manufacturing, cost, or commercial concepts.
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .presentation_binding import PresentationStateResolver
from .presentation_state import FurniturePresentationState
from .presentation_visual_contract import (
    PresentationVisualContract,
    resolve_visual_contract,
)


# ── Helpers ──────────────────────────────────────────────────────────


def _ensure_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string, got {type(value).__name__}")
    return value


def _ensure_frozenset(value: Any, field_name: str) -> frozenset[str]:
    if value is None:
        return frozenset()
    if isinstance(value, frozenset):
        return value
    if isinstance(value, (set, list, tuple)):
        return frozenset(str(v) for v in value)
    raise TypeError(
        f"{field_name} must be a frozenset, set, list, or tuple, "
        f"got {type(value).__name__}"
    )


# ── Snapshot dataclass ───────────────────────────────────────────────


@dataclass(frozen=True)
class SynchronizedPresentation:
    """Read-only snapshot of a single component's synchronized presentation.

    Consolidates the result of running the full presentation pipeline
    (binding → visual contract) for one component ID.

    All fields are derived from the pipeline outputs — no lifecycle
    methods, no mutation, no engine patterns.
    """

    component_id: str = ""
    presentation_state: FurniturePresentationState = field(
        default_factory=FurniturePresentationState
    )
    visual_contract: PresentationVisualContract = field(
        default_factory=PresentationVisualContract
    )

    def __post_init__(self):
        object.__setattr__(
            self, "component_id", _ensure_str(self.component_id, "component_id")
        )
        if not isinstance(self.presentation_state, FurniturePresentationState):
            object.__setattr__(self, "presentation_state", FurniturePresentationState())
        if not isinstance(self.visual_contract, PresentationVisualContract):
            object.__setattr__(self, "visual_contract", PresentationVisualContract())

    # ── Convenience delegations ───────────────────────────────────

    @property
    def dominant_flag(self) -> str:
        """Delegates to the presentation state's dominant_flag."""
        return self.presentation_state.dominant_flag

    @property
    def visual_severity(self) -> int:
        """Delegates to the presentation state's visual_severity."""
        return self.presentation_state.visual_severity

    @property
    def is_neutral(self) -> bool:
        """True when both presentation state and visual contract are neutral."""
        return self.presentation_state.is_neutral and self.visual_contract.is_neutral


# ── Synchronization function ─────────────────────────────────────────


def synchronize_presentation(
    component_ids: tuple[str, ...],
    *,
    selected_ids: frozenset[str] | None = None,
    hovered_id: str = "",
    focused_id: str = "",
    disabled_ids: frozenset[str] | None = None,
    warning_ids: frozenset[str] | None = None,
    error_ids: frozenset[str] | None = None,
    preview_ids: frozenset[str] | None = None,
    active_ids: frozenset[str] | None = None,
    muted_ids: frozenset[str] | None = None,
) -> tuple[SynchronizedPresentation, ...]:
    """Run the full presentation pipeline for a set of component IDs.

    1. Creates a PresentationStateResolver with the given flag sets.
    2. Resolves FurniturePresentationState for each component ID.
    3. Resolves PresentationVisualContract for each state.
    4. Bundles the results into SynchronizedPresentation snapshots.

    Parameters
    ----------
    component_ids : Component IDs to synchronize.
    All other parameters : The presentation flag ID sets (same as
        PresentationStateResolver / resolve_presentation_state).

    Returns
    -------
    One SynchronizedPresentation per component ID, preserving order.

    The function is deterministic and side-effect free. It creates no
    global state, engines, event buses, or workflows.
    """
    if not component_ids:
        return ()

    resolver = PresentationStateResolver(
        selected_ids=_ensure_frozenset(selected_ids, "selected_ids"),
        hovered_id=_ensure_str(hovered_id, "hovered_id"),
        focused_id=_ensure_str(focused_id, "focused_id"),
        disabled_ids=_ensure_frozenset(disabled_ids, "disabled_ids"),
        warning_ids=_ensure_frozenset(warning_ids, "warning_ids"),
        error_ids=_ensure_frozenset(error_ids, "error_ids"),
        preview_ids=_ensure_frozenset(preview_ids, "preview_ids"),
        active_ids=_ensure_frozenset(active_ids, "active_ids"),
        muted_ids=_ensure_frozenset(muted_ids, "muted_ids"),
    )

    states = resolver.resolve_all(component_ids)

    return tuple(
        SynchronizedPresentation(
            component_id=cid,
            presentation_state=state,
            visual_contract=resolve_visual_contract(state),
        )
        for cid, state in zip(component_ids, states)
    )


# ── Integration helper ──────────────────────────────────────────────


def synchronize_descriptor_pairs(
    snapshot: SynchronizedPresentation | None,
) -> tuple[tuple[str, str], ...]:
    """Flatten a synchronize snapshot into display metadata pairs.

    Returns () for None or neutral.
    """
    if snapshot is None or snapshot.is_neutral:
        return ()
    pairs: list[tuple[str, str]] = [
        ("component_id", snapshot.component_id),
        ("sync_dominant", snapshot.dominant_flag),
        ("sync_severity", str(snapshot.visual_severity)),
    ]
    if snapshot.presentation_state.active_flags:
        flags = ",".join(snapshot.presentation_state.active_flags)
        pairs.append(("sync_flags", flags))
    return tuple(pairs)


__all__ = [
    "SynchronizedPresentation",
    "synchronize_presentation",
    "synchronize_descriptor_pairs",
]
