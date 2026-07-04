# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Furniture Presentation State System
#
# A value-object style presentation-state resolver for furniture UI
# components.  Derives visual UI flags (selected, hovered, focused,
# disabled, warning, error, preview, active, muted) from simple
# ID-based inputs.
#
# This is a pure data/resolver layer:
#   - no renderer
#   - no engine
#   - no event bus
#   - no workflow
#   - no service registry
#   - no domain, engineering, manufacturing, cost, or commercial models
#
# The resolver is deterministic and side-effect free.
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ── Canonical flag list & visual severity ordering ───────────────────

PRESENTATION_FLAGS: tuple[str, ...] = (
    "selected",
    "hovered",
    "focused",
    "disabled",
    "warning",
    "error",
    "preview",
    "active",
    "muted",
)

_VISUAL_SEVERITY: dict[str, int] = {
    "error": 50,
    "warning": 40,
    "disabled": 30,
    "selected": 25,
    "hovered": 20,
    "focused": 20,
    "preview": 10,
    "active": 5,
    "muted": 1,
}


# ── Helpers ──────────────────────────────────────────────────────────


def _ensure_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be a bool, got {type(value).__name__}")
    return value


def _ensure_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string, got {type(value).__name__}")
    return value


# ── Value-object dataclass ───────────────────────────────────────────


@dataclass(frozen=True)
class FurniturePresentationState:
    """Value-object presentation state for a single furniture UI component.

    Each flag is a bool. The state is frozen and immutable.
    Use ``resolve_presentation_state()`` to derive an instance from
    ID-based inputs.

    No business, manufacturing, cost, or commercial concepts.
    """

    selected: bool = False
    hovered: bool = False
    focused: bool = False
    disabled: bool = False
    warning: bool = False
    error: bool = False
    preview: bool = False
    active: bool = False
    muted: bool = False

    def __post_init__(self):
        for flag in PRESENTATION_FLAGS:
            value = getattr(self, flag, None)
            if value is not None:
                object.__setattr__(self, flag, _ensure_bool(value, flag))

    # ── Derived properties ───────────────────────────────────────

    @property
    def is_neutral(self) -> bool:
        """True when no flags are active — the component is in its resting UI state."""
        return not any(
            getattr(self, flag, False) for flag in PRESENTATION_FLAGS
        )

    @property
    def active_flags(self) -> tuple[str, ...]:
        """Return only the flags that are set to True, in canonical order."""
        return tuple(
            flag for flag in PRESENTATION_FLAGS if getattr(self, flag, False)
        )

    @property
    def visual_severity(self) -> int:
        """Highest visual severity among active flags.

        Higher values demand more urgent visual treatment.
        0 when neutral.
        """
        if self.is_neutral:
            return 0
        return max(
            _VISUAL_SEVERITY.get(flag, 0)
            for flag in self.active_flags
        )

    @property
    def dominant_flag(self) -> str:
        """The single most visually significant active flag.

        Returns ``"neutral"`` when no flags are active.
        Ties are broken by canonical flag order (first wins).
        """
        if self.is_neutral:
            return "neutral"
        best_flag = "neutral"
        best_sev = -1
        for flag in self.active_flags:
            sev = _VISUAL_SEVERITY.get(flag, 0)
            if sev > best_sev:
                best_sev = sev
                best_flag = flag
        return best_flag

    def __repr__(self) -> str:
        active = self.active_flags
        if not active:
            return "FurniturePresentationState(neutral)"
        return f"FurniturePresentationState({', '.join(active)})"


# ── Sentinel for no-component states ────────────────────────────────

_NEUTRAL: FurniturePresentationState | None = None


def neutral_presentation_state() -> FurniturePresentationState:
    """Return a shared neutral state singleton."""
    global _NEUTRAL
    if _NEUTRAL is None:
        _NEUTRAL = FurniturePresentationState()
    return _NEUTRAL


# ── Resolver ────────────────────────────────────────────────────────


def resolve_presentation_state(
    component_id: str,
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
) -> FurniturePresentationState:
    """Derive a presentation state for a single component ID.

    Parameters
    ----------
    component_id : The component to resolve state for.
    selected_ids : Set of currently selected component IDs.
    hovered_id : Component ID under cursor (single).
    focused_id : Component ID with keyboard focus (single).
    disabled_ids : Set of currently disabled component IDs.
    warning_ids : Set of components with warning-level issues.
    error_ids : Set of components with error-level issues.
    preview_ids : Set of components in preview mode.
    active_ids : Set of currently active component IDs.
    muted_ids : Set of muted component IDs.

    Returns
    -------
    A frozen FurniturePresentationState for *component_id*.

    The resolver is deterministic and side-effect free.
    Repeated calls with the same inputs produce the same result.
    """
    _ensure_str(component_id, "component_id")

    selected = bool(component_id in (selected_ids or frozenset()))
    hovered = bool(component_id == hovered_id and component_id)
    focused = bool(component_id == focused_id and component_id)
    disabled = bool(component_id in (disabled_ids or frozenset()))
    warning = bool(component_id in (warning_ids or frozenset()))
    error = bool(component_id in (error_ids or frozenset()))
    preview = bool(component_id in (preview_ids or frozenset()))
    active = bool(component_id in (active_ids or frozenset()))
    muted = bool(component_id in (muted_ids or frozenset()))

    return FurniturePresentationState(
        selected=selected,
        hovered=hovered,
        focused=focused,
        disabled=disabled,
        warning=warning,
        error=error,
        preview=preview,
        active=active,
        muted=muted,
    )


def resolve_presentation_states(
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
) -> tuple[FurniturePresentationState, ...]:
    """Batch-resolve presentation states for many component IDs.

    Preserves order and cardinality of *component_ids*.
    """
    return tuple(
        resolve_presentation_state(
            cid,
            selected_ids=selected_ids,
            hovered_id=hovered_id,
            focused_id=focused_id,
            disabled_ids=disabled_ids,
            warning_ids=warning_ids,
            error_ids=error_ids,
            preview_ids=preview_ids,
            active_ids=active_ids,
            muted_ids=muted_ids,
        )
        for cid in component_ids
    )


# ── Integration helpers ──────────────────────────────────────────────


def presentation_state_descriptor_pairs(
    state: FurniturePresentationState | None,
) -> tuple[tuple[str, str], ...]:
    """Flatten a presentation state into display metadata pairs.

    Returns () for None or neutral state.
    """
    if state is None or state.is_neutral:
        return ()
    pairs: list[tuple[str, str]] = []
    for flag in state.active_flags:
        pairs.append((f"presentation_{flag}", "yes"))
    pairs.append(("presentation_dominant", state.dominant_flag))
    pairs.append(("presentation_severity", str(state.visual_severity)))
    return tuple(pairs)


# ── __all__ ─────────────────────────────────────────────────────────

__all__ = [
    "PRESENTATION_FLAGS",
    "FurniturePresentationState",
    "neutral_presentation_state",
    "resolve_presentation_state",
    "resolve_presentation_states",
    "presentation_state_descriptor_pairs",
]
