# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Interactive Furniture Components
#
# Visual Components define WHAT furniture element exists.
# Furniture Visual Styles describe HOW that element should appear.
# Interactive Components define presentation-only interaction state.
#
# These are presentation-only dataclasses — no geometry, no positions,
# no transforms, no FreeCAD, no SceneNode, no backend mutation.
#
# Anything that would require engine-level hit testing or spatial
# queries is left to a future renderer.
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .visual_components import (
    DoorVisualComponent,
    DrawerVisualComponent,
    FeatureMarkerComponent,
    HardwareVisualComponent,
    VisualComponent,
)

# ── Interaction states ───────────────────────────────────────────────

INTERACTIVE_STATES = (
    "NORMAL",
    "SELECTED",
    "HIGHLIGHTED",
    "EXPANDED",
    "COLLAPSED",
    "HIDDEN",
    "UNSUPPORTED",
    "STALE",
)

# ── Helper validators ───────────────────────────────────────────────


def _ensure_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string, got {type(value).__name__}")
    return value


def _ensure_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be a bool, got {type(value).__name__}")
    return value


def _ensure_string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (_ensure_str(value, field_name),)
    return tuple(_ensure_str(str(item), field_name) for item in value)


def _ensure_state(value: Any, field_name: str) -> str:
    state = _ensure_str(value, field_name).upper()
    if state not in INTERACTIVE_STATES:
        raise TypeError(
            f"{field_name} must be one of {INTERACTIVE_STATES}, got {state!r}"
        )
    return state


# ── Sub-dataclasses ─────────────────────────────────────────────────


@dataclass(frozen=True)
class ComponentInteractionOverlay:
    """Presentation-only selection/highlight/expand state.

    All fields are bools — no geometry, no transforms, no backend.
    """

    selected: bool = False
    highlighted: bool = False
    expanded: bool = False

    def __post_init__(self):
        object.__setattr__(self, "selected", _ensure_bool(self.selected, "selected"))
        object.__setattr__(
            self, "highlighted", _ensure_bool(self.highlighted, "highlighted")
        )
        object.__setattr__(self, "expanded", _ensure_bool(self.expanded, "expanded"))


@dataclass(frozen=True)
class ComponentVisibilityState:
    """Presentation-only visibility toggles for a furniture component.

    ``hardware_visible`` and ``feature_markers_visible`` are context-
    dependent — they only apply when the component type supports them.
    ``door_swing_visible`` and ``drawer_open_visible`` are motion
    indicators that hint at hinge/swing and rail extension arcs.
    """

    visible: bool = True
    hardware_visible: bool = True
    feature_markers_visible: bool = True
    door_swing_visible: bool = False
    drawer_open_visible: bool = False

    def __post_init__(self):
        object.__setattr__(self, "visible", _ensure_bool(self.visible, "visible"))
        object.__setattr__(
            self,
            "hardware_visible",
            _ensure_bool(self.hardware_visible, "hardware_visible"),
        )
        object.__setattr__(
            self,
            "feature_markers_visible",
            _ensure_bool(self.feature_markers_visible, "feature_markers_visible"),
        )
        object.__setattr__(
            self,
            "door_swing_visible",
            _ensure_bool(self.door_swing_visible, "door_swing_visible"),
        )
        object.__setattr__(
            self,
            "drawer_open_visible",
            _ensure_bool(self.drawer_open_visible, "drawer_open_visible"),
        )


@dataclass(frozen=True)
class ComponentMotionIndicator:
    """Presentation-only motion hint for a furniture component.

    Values are descriptive strings, e.g. ``"swing"``, ``"slide"``,
    ``"lift"``, ``"none"``. No animation engine, no geometry.
    """

    motion_hint: str = ""

    def __post_init__(self):
        object.__setattr__(
            self, "motion_hint", _ensure_str(self.motion_hint, "motion_hint")
        )


@dataclass(frozen=True)
class ComponentInteractionState:
    """Aggregate interaction state for a single furniture component.

    Combines overlay (selected/highlighted/expanded), visibility
    toggles, a motion hint, display tooltip, warnings, and a
    source reference. All fields are presentation-only.
    """

    overlay: ComponentInteractionOverlay = field(
        default_factory=ComponentInteractionOverlay
    )
    visibility: ComponentVisibilityState = field(
        default_factory=ComponentVisibilityState
    )
    motion: ComponentMotionIndicator = field(
        default_factory=ComponentMotionIndicator
    )
    state_label: str = "NORMAL"
    tooltip: str = ""
    warnings: tuple[str, ...] = field(default_factory=tuple)
    source_reference: str = ""

    def __post_init__(self):
        if not isinstance(self.overlay, ComponentInteractionOverlay):
            object.__setattr__(self, "overlay", ComponentInteractionOverlay())
        if not isinstance(self.visibility, ComponentVisibilityState):
            object.__setattr__(self, "visibility", ComponentVisibilityState())
        if not isinstance(self.motion, ComponentMotionIndicator):
            object.__setattr__(self, "motion", ComponentMotionIndicator())
        object.__setattr__(
            self, "state_label", _ensure_state(self.state_label, "state_label")
        )
        object.__setattr__(self, "tooltip", _ensure_str(self.tooltip, "tooltip"))
        object.__setattr__(
            self,
            "warnings",
            _ensure_string_tuple(self.warnings, "warnings"),
        )
        object.__setattr__(
            self,
            "source_reference",
            _ensure_str(self.source_reference, "source_reference"),
        )


# ── Top-level interactive component ─────────────────────────────────


@dataclass(frozen=True)
class InteractiveVisualComponent:
    """Presentation-only interactive wrapper for a furniture component.

    Wraps the identity (component_id, component_type, display_name)
    from the source VisualComponent with an aggregate ComponentInteractionState.

    No geometry, no transforms, no FreeCAD objects, no SceneNode.
    """

    component_id: str = ""
    component_type: str = ""
    display_name: str = ""
    interaction: ComponentInteractionState = field(
        default_factory=ComponentInteractionState
    )

    def __post_init__(self):
        object.__setattr__(
            self, "component_id", _ensure_str(self.component_id, "component_id")
        )
        object.__setattr__(
            self,
            "component_type",
            _ensure_str(self.component_type, "component_type"),
        )
        object.__setattr__(
            self, "display_name", _ensure_str(self.display_name, "display_name")
        )
        if not isinstance(self.interaction, ComponentInteractionState):
            object.__setattr__(self, "interaction", ComponentInteractionState())


# ── State helpers ───────────────────────────────────────────────────


def _derive_state_label(
    component: VisualComponent,
    *,
    overlay: ComponentInteractionOverlay,
    visibility: ComponentVisibilityState,
) -> str:
    """Derive an interaction state label from a VisualComponent and overlay."""
    if not visibility.visible:
        return "HIDDEN"
    state = (component.display_state or "NORMAL").upper()
    if state in ("UNSUPPORTED", "STALE"):
        return state
    if overlay.expanded:
        return "EXPANDED"
    if overlay.highlighted:
        return "HIGHLIGHTED"
    if overlay.selected:
        return "SELECTED"
    if state == "HIDDEN":
        return "HIDDEN"
    return "NORMAL"


def _type_supports_hardware(component_type: str) -> bool:
    return component_type == "HARDWARE" or component_type in (
        "DOOR",
        "DRAWER",
        "CABINET",
    )


def _type_supports_feature_markers(component_type: str) -> bool:
    return component_type == "FEATURE_MARKER"


# ── Builder ─────────────────────────────────────────────────────────


def build_interactive_visual_components(
    components: tuple[VisualComponent, ...],
    *,
    selected_component_id: str = "",
    highlighted_component_id: str = "",
    show_hardware: bool = True,
    show_feature_markers: bool = True,
    show_door_swing: bool = False,
    show_drawer_open: bool = False,
) -> tuple[InteractiveVisualComponent, ...]:
    """Build interactive wrappers for a sequence of VisualComponents.

    Preserves 1:1 mapping with the input.

    Parameters
    ----------
    components : VisualComponent sequence to wrap.
    selected_component_id : Component id to mark as selected.
    highlighted_component_id : Component id to mark as highlighted.
    show_hardware : Global toggle for hardware visibility.
    show_feature_markers : Global toggle for feature marker visibility.
    show_door_swing : Show door swing arcs (doors only).
    show_drawer_open : Show drawer open indicators (drawers only).

    Returns
    -------
    One InteractiveVisualComponent per input VisualComponent.
    """
    if not components:
        return ()

    result: list[InteractiveVisualComponent] = []

    for component in components:
        if not isinstance(component, VisualComponent):
            raise TypeError(
                "components must contain VisualComponent instances"
            )

        ctype = component.component_type
        cid = component.id or ""
        visibility = component.visibility if hasattr(component, "visibility") else True

        # ── overlay ──────────────────────────────────────────────
        overlay = ComponentInteractionOverlay(
            selected=bool(cid and cid == selected_component_id),
            highlighted=bool(cid and cid == highlighted_component_id),
            expanded=False,  # Not derived from source — toggle state
        )

        # ── visibility toggles ───────────────────────────────────
        type_specific_hw_visible = show_hardware
        if not _type_supports_hardware(ctype):
            type_specific_hw_visible = False

        type_specific_fm_visible = show_feature_markers
        if not _type_supports_feature_markers(ctype):
            type_specific_fm_visible = False

        door_swing = bool(
            show_door_swing and ctype == "DOOR"
        )
        drawer_open = bool(
            show_drawer_open and ctype == "DRAWER"
        )

        vis = ComponentVisibilityState(
            visible=bool(visibility),
            hardware_visible=type_specific_hw_visible,
            feature_markers_visible=type_specific_fm_visible,
            door_swing_visible=door_swing,
            drawer_open_visible=drawer_open,
        )

        # ── motion hint ──────────────────────────────────────────
        if ctype == "DOOR" and door_swing:
            motion_hint = "swing"
        elif ctype == "DRAWER" and drawer_open:
            motion_hint = "slide"
        else:
            motion_hint = ""

        motion = ComponentMotionIndicator(motion_hint=motion_hint)

        # ── state label ──────────────────────────────────────────
        state_label = _derive_state_label(
            component, overlay=overlay, visibility=vis
        )

        # ── interaction state ────────────────────────────────────
        interaction = ComponentInteractionState(
            overlay=overlay,
            visibility=vis,
            motion=motion,
            state_label=state_label,
            tooltip=component.tooltip if hasattr(component, "tooltip") else "",
            warnings=component.warnings if hasattr(component, "warnings") else (),
            source_reference=(
                component.source_reference
                if hasattr(component, "source_reference")
                else ""
            ),
        )

        result.append(
            InteractiveVisualComponent(
                component_id=cid,
                component_type=ctype,
                display_name=(
                    component.display_name
                    if hasattr(component, "display_name")
                    else component.id
                ),
                interaction=interaction,
            )
        )

    return tuple(result)


# ── Metadata helpers ────────────────────────────────────────────────


def interaction_descriptor_pairs(
    interactive: InteractiveVisualComponent | None,
) -> tuple[tuple[str, str], ...]:
    """Flatten an InteractiveVisualComponent into display metadata pairs."""
    if interactive is None:
        return ()

    pairs: list[tuple[str, str]] = []
    interaction = interactive.interaction

    pairs.append(("interaction_state", interaction.state_label))

    overlay = interaction.overlay
    pairs.append(("selected", "yes" if overlay.selected else "no"))
    pairs.append(("highlighted", "yes" if overlay.highlighted else "no"))
    pairs.append(("expanded", "yes" if overlay.expanded else "no"))

    vis = interaction.visibility
    pairs.append(("visible", "yes" if vis.visible else "no"))
    pairs.append(("hardware_visible", "yes" if vis.hardware_visible else "no"))
    pairs.append(
        ("feature_markers_visible", "yes" if vis.feature_markers_visible else "no")
    )
    pairs.append(
        ("door_swing_visible", "yes" if vis.door_swing_visible else "no")
    )
    pairs.append(
        ("drawer_open_visible", "yes" if vis.drawer_open_visible else "no")
    )

    motion = interaction.motion
    if motion.motion_hint:
        pairs.append(("motion_hint", motion.motion_hint))

    if interaction.warnings:
        for w in interaction.warnings:
            pairs.append(("iwarning", str(w)))

    return tuple(pairs)


def interaction_summary_label(
    interactive: InteractiveVisualComponent | None,
) -> str:
    """Return a single-line human-readable summary of interaction state."""
    if interactive is None:
        return "No interactive state"

    i = interactive.interaction
    parts = [interactive.component_type or "?", i.state_label or "NORMAL"]

    if i.overlay.selected:
        parts.append("selected")
    if i.overlay.highlighted:
        parts.append("highlighted")
    if i.overlay.expanded:
        parts.append("expanded")
    if not i.visibility.visible:
        parts.append("hidden")

    motion = i.motion.motion_hint
    if motion:
        parts.append(motion)

    return " | ".join(parts)


def count_active_interactions(
    interactives: tuple[InteractiveVisualComponent, ...],
) -> dict[str, int]:
    """Count components by interaction state label."""
    counts: dict[str, int] = {}
    for ic in interactives:
        label = ic.interaction.state_label
        counts[label] = counts.get(label, 0) + 1
    return counts


__all__ = [
    "INTERACTIVE_STATES",
    "ComponentInteractionOverlay",
    "ComponentVisibilityState",
    "ComponentMotionIndicator",
    "ComponentInteractionState",
    "InteractiveVisualComponent",
    "build_interactive_visual_components",
    "interaction_descriptor_pairs",
    "interaction_summary_label",
    "count_active_interactions",
]
