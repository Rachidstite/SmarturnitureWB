# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Presentation State Binding Layer
#
# Binds existing Configurator V2 UI state sources to
# FurniturePresentationState without duplicating resolution logic
# inside components.
#
# This is a thin adapter layer — it reuses:
#   - FurniturePresentationState
#   - resolve_presentation_state
#   - resolve_presentation_states
#
# It does NOT create:
#   - PresentationEngine
#   - StateEngine
#   - Workflow
#   - EventBus
#   - Renderer
#   - Service registry
#
# No domain, manufacturing, cost, or commercial concepts.
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .interactive_components import InteractiveVisualComponent
from .presentation_state import (
    FurniturePresentationState,
    resolve_presentation_state,
    resolve_presentation_states,
)
from .visual_components import VisualComponent


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


# ── PresentationStateResolver class ──────────────────────────────────


@dataclass
class PresentationStateResolver:
    """Encapsulates presentation flag ID sets and provides convenience
    resolve and bind methods.

    Once constructed, the flag sets are fixed and subsequent calls to
    ``resolve``, ``resolve_all``, and ``bind_to_interactive`` are
    deterministic and side-effect free.

    Examples
    --------
    >>> resolver = PresentationStateResolver(
    ...     selected_ids=frozenset({"door-1", "drawer-1"}),
    ...     warning_ids=frozenset({"panel-1"}),
    ... )
    >>> state = resolver.resolve("door-1")
    >>> state.selected
    True
    >>> interactives = resolver.bind_to_interactive(components)
    """

    selected_ids: frozenset[str] = field(default_factory=frozenset)
    hovered_id: str = ""
    focused_id: str = ""
    disabled_ids: frozenset[str] = field(default_factory=frozenset)
    warning_ids: frozenset[str] = field(default_factory=frozenset)
    error_ids: frozenset[str] = field(default_factory=frozenset)
    preview_ids: frozenset[str] = field(default_factory=frozenset)
    active_ids: frozenset[str] = field(default_factory=frozenset)
    muted_ids: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self):
        self.selected_ids = _ensure_frozenset(self.selected_ids, "selected_ids")
        self.hovered_id = _ensure_str(self.hovered_id, "hovered_id")
        self.focused_id = _ensure_str(self.focused_id, "focused_id")
        self.disabled_ids = _ensure_frozenset(self.disabled_ids, "disabled_ids")
        self.warning_ids = _ensure_frozenset(self.warning_ids, "warning_ids")
        self.error_ids = _ensure_frozenset(self.error_ids, "error_ids")
        self.preview_ids = _ensure_frozenset(self.preview_ids, "preview_ids")
        self.active_ids = _ensure_frozenset(self.active_ids, "active_ids")
        self.muted_ids = _ensure_frozenset(self.muted_ids, "muted_ids")

    # ── Single-component resolve ──────────────────────────────────

    def resolve(self, component_id: str) -> FurniturePresentationState:
        """Resolve presentation state for a single component ID.

        Deterministic — repeated calls with the same resolver and ID
        produce the same result.
        """
        return resolve_presentation_state(
            component_id,
            selected_ids=self.selected_ids,
            hovered_id=self.hovered_id,
            focused_id=self.focused_id,
            disabled_ids=self.disabled_ids,
            warning_ids=self.warning_ids,
            error_ids=self.error_ids,
            preview_ids=self.preview_ids,
            active_ids=self.active_ids,
            muted_ids=self.muted_ids,
        )

    # ── Batch resolve ─────────────────────────────────────────────

    def resolve_all(
        self, component_ids: tuple[str, ...]
    ) -> tuple[FurniturePresentationState, ...]:
        """Resolve presentation states for multiple component IDs.

        Preserves order and cardinality of *component_ids*.
        """
        return resolve_presentation_states(
            component_ids,
            selected_ids=self.selected_ids,
            hovered_id=self.hovered_id,
            focused_id=self.focused_id,
            disabled_ids=self.disabled_ids,
            warning_ids=self.warning_ids,
            error_ids=self.error_ids,
            preview_ids=self.preview_ids,
            active_ids=self.active_ids,
            muted_ids=self.muted_ids,
        )

    # ── Bind to InteractiveVisualComponents ───────────────────────

    def bind_to_interactive(
        self,
        interactives: tuple[InteractiveVisualComponent, ...],
    ) -> tuple[InteractiveVisualComponent, ...]:
        """Attach resolved presentation state to each interactive component.

        Returns new InteractiveVisualComponent instances with the
        ``presentation`` field populated. The original sequence is
        unchanged (frozen dataclasses).
        """
        if not interactives:
            return ()

        ids = tuple(ic.component_id for ic in interactives)
        states = self.resolve_all(ids)

        result: list[InteractiveVisualComponent] = []
        for ic, state in zip(interactives, states):
            result.append(
                InteractiveVisualComponent(
                    component_id=ic.component_id,
                    component_type=ic.component_type,
                    display_name=ic.display_name,
                    interaction=type(ic.interaction)(
                        overlay=ic.interaction.overlay,
                        visibility=ic.interaction.visibility,
                        motion=ic.interaction.motion,
                        state_label=ic.interaction.state_label,
                        tooltip=ic.interaction.tooltip,
                        warnings=ic.interaction.warnings,
                        source_reference=ic.interaction.source_reference,
                        presentation=state if not state.is_neutral else None,
                    ),
                )
            )
        return tuple(result)

    # ── Alternative factory ───────────────────────────────────────

    @classmethod
    def from_visual_components_and_ids(
        cls,
        components: tuple[VisualComponent, ...],
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
        """Convenience: resolve states for VisualComponents by their IDs.

        Returns one FurniturePresentationState per component, preserving
        order. Components whose IDs don't appear in any flag set receive
        neutral states.
        """
        ids = tuple(c.id for c in components)
        return resolve_presentation_states(
            ids,
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


__all__ = [
    "PresentationStateResolver",
]
