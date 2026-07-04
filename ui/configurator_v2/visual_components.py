from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from typing import Any

from .scene_projection import SceneBoundsProjection, SceneProjection

VISUAL_COMPONENT_STATES = (
    "NORMAL",
    "SELECTED",
    "HIGHLIGHTED",
    "HIDDEN",
    "UNSUPPORTED",
    "STALE",
)


def _ensure_str(value, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    return value


def _ensure_bool(value, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be a bool")
    return value


def _ensure_string_pairs(value, field_name: str) -> tuple[tuple[str, str], ...]:
    if value is None:
        return ()
    pairs = []
    for item in value:
        if isinstance(item, Mapping):
            key = item.get("name", item.get("label", item.get("key", "")))
            pair_value = item.get("value", item.get("text", ""))
        elif isinstance(item, tuple) and len(item) == 2:
            key, pair_value = item
        else:
            key = getattr(item, "name", getattr(item, "label", getattr(item, "key", "")))
            pair_value = getattr(item, "value", getattr(item, "text", ""))
        pairs.append((_ensure_str(str(key), f"{field_name}.key"), _ensure_str(str(pair_value), f"{field_name}.value")))
    return tuple(pairs)


def _ensure_string_tuple(value, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (_ensure_str(value, field_name),)
    return tuple(_ensure_str(str(item), field_name) for item in value)


def _ensure_bounds(value, field_name: str) -> SceneBoundsProjection:
    if isinstance(value, SceneBoundsProjection):
        return value
    if value is None:
        return SceneBoundsProjection()
    if isinstance(value, Mapping):
        return SceneBoundsProjection(
            minimum=value.get("minimum", (0.0, 0.0, 0.0)),
            maximum=value.get("maximum", (0.0, 0.0, 0.0)),
            source_reference=value.get("source_reference", ""),
        )
    raise TypeError(f"{field_name} must be a SceneBoundsProjection")


def _reject_backend_like_object(value: Any, field_name: str):
    if value is None:
        return
    value_type = type(value)
    module_name = getattr(value_type, "__module__", "")
    if module_name.startswith(("FreeCAD", "Part", "Sketcher")):
        raise TypeError(f"{field_name} cannot contain backend geometry objects")
    if any(hasattr(value, attr) for attr in ("Shape", "ViewObject", "Document")):
        raise TypeError(f"{field_name} cannot contain backend geometry objects")


def _ensure_state(value: str, field_name: str) -> str:
    state = _ensure_str(value, field_name).upper()
    if state not in VISUAL_COMPONENT_STATES:
        raise TypeError(f"{field_name} must be one of {VISUAL_COMPONENT_STATES}")
    return state


@dataclass(frozen=True)
class VisualComponent:
    id: str = ""
    display_name: str = ""
    component_type: str = ""
    color: str = ""
    material_name: str = ""
    visibility: bool = True
    selection_state: str = "NORMAL"
    highlight_state: str = "NORMAL"
    display_state: str = "NORMAL"
    bounding_box: SceneBoundsProjection = field(default_factory=SceneBoundsProjection)
    display_metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    representation_status: str = "Unavailable"
    base_color: str = ""
    accent_color: str = ""
    icon_name: str = ""
    label: str = ""
    tooltip: str = ""
    future_theme_key: str = ""
    source_reference: str = ""

    def __post_init__(self):
        object.__setattr__(self, "id", _ensure_str(self.id, "id"))
        object.__setattr__(self, "display_name", _ensure_str(self.display_name, "display_name"))
        object.__setattr__(self, "component_type", _ensure_str(self.component_type, "component_type"))
        object.__setattr__(self, "color", _ensure_str(self.color, "color"))
        object.__setattr__(self, "material_name", _ensure_str(self.material_name, "material_name"))
        object.__setattr__(self, "visibility", _ensure_bool(self.visibility, "visibility"))
        object.__setattr__(self, "selection_state", _ensure_state(self.selection_state, "selection_state"))
        object.__setattr__(self, "highlight_state", _ensure_state(self.highlight_state, "highlight_state"))
        object.__setattr__(self, "display_state", _ensure_state(self.display_state, "display_state"))
        object.__setattr__(self, "bounding_box", _ensure_bounds(self.bounding_box, "bounding_box"))
        object.__setattr__(self, "display_metadata", _ensure_string_pairs(self.display_metadata, "display_metadata"))
        object.__setattr__(self, "warnings", _ensure_string_tuple(self.warnings, "warnings"))
        object.__setattr__(self, "representation_status", _ensure_str(self.representation_status, "representation_status"))
        object.__setattr__(self, "base_color", _ensure_str(self.base_color, "base_color"))
        object.__setattr__(self, "accent_color", _ensure_str(self.accent_color, "accent_color"))
        object.__setattr__(self, "icon_name", _ensure_str(self.icon_name, "icon_name"))
        object.__setattr__(self, "label", _ensure_str(self.label, "label"))
        object.__setattr__(self, "tooltip", _ensure_str(self.tooltip, "tooltip"))
        object.__setattr__(self, "future_theme_key", _ensure_str(self.future_theme_key, "future_theme_key"))
        object.__setattr__(self, "source_reference", _ensure_str(self.source_reference, "source_reference"))


@dataclass(frozen=True)
class CabinetVisualComponent(VisualComponent):
    component_type: str = "CABINET"
    icon_name: str = "cabinet"
    future_theme_key: str = "furniture.cabinet"


@dataclass(frozen=True)
class PanelVisualComponent(VisualComponent):
    component_type: str = "PANEL"
    icon_name: str = "panel"
    future_theme_key: str = "furniture.panel"


@dataclass(frozen=True)
class DoorVisualComponent(VisualComponent):
    component_type: str = "DOOR"
    icon_name: str = "door"
    future_theme_key: str = "furniture.door"


@dataclass(frozen=True)
class DrawerVisualComponent(VisualComponent):
    component_type: str = "DRAWER"
    icon_name: str = "drawer"
    future_theme_key: str = "furniture.drawer"


@dataclass(frozen=True)
class ShelfVisualComponent(VisualComponent):
    component_type: str = "SHELF"
    icon_name: str = "shelf"
    future_theme_key: str = "furniture.shelf"


@dataclass(frozen=True)
class DividerVisualComponent(VisualComponent):
    component_type: str = "DIVIDER"
    icon_name: str = "divider"
    future_theme_key: str = "furniture.divider"


@dataclass(frozen=True)
class BackPanelVisualComponent(VisualComponent):
    component_type: str = "BACK_PANEL"
    icon_name: str = "back-panel"
    future_theme_key: str = "furniture.back-panel"


@dataclass(frozen=True)
class HardwareVisualComponent(VisualComponent):
    component_type: str = "HARDWARE"
    icon_name: str = "hardware"
    future_theme_key: str = "furniture.hardware"


@dataclass(frozen=True)
class FeatureMarkerComponent(VisualComponent):
    component_type: str = "FEATURE_MARKER"
    icon_name: str = "feature-marker"
    future_theme_key: str = "furniture.feature-marker"


_COMPONENT_CLASS_BY_TYPE = {
    "CABINET": CabinetVisualComponent,
    "PANEL": PanelVisualComponent,
    "DOOR": DoorVisualComponent,
    "DRAWER": DrawerVisualComponent,
    "SHELF": ShelfVisualComponent,
    "DIVIDER": DividerVisualComponent,
    "BACK_PANEL": BackPanelVisualComponent,
    "HARDWARE": HardwareVisualComponent,
    "FEATURE_MARKER": FeatureMarkerComponent,
}

_STYLE_BY_TYPE = {
    "CABINET": {"base_color": "#C8A26E", "accent_color": "#7A5330"},
    "PANEL": {"base_color": "#D9CBB8", "accent_color": "#8E7A63"},
    "DOOR": {"base_color": "#B9825A", "accent_color": "#5B3A29"},
    "DRAWER": {"base_color": "#9B8C7A", "accent_color": "#4B4137"},
    "SHELF": {"base_color": "#D4B07A", "accent_color": "#6D5332"},
    "DIVIDER": {"base_color": "#CBB7A0", "accent_color": "#6D6151"},
    "BACK_PANEL": {"base_color": "#B4A58F", "accent_color": "#64594C"},
    "HARDWARE": {"base_color": "#8A9199", "accent_color": "#43484E"},
    "FEATURE_MARKER": {"base_color": "#4D89C7", "accent_color": "#1E4D7A"},
}


def _metadata_lookup(component_metadata: tuple[tuple[str, str], ...]) -> dict[str, str]:
    return {key.lower(): value for key, value in component_metadata}


def _component_type_from_node_type(node_type: str, metadata: tuple[tuple[str, str], ...]) -> str:
    probe = f"{node_type} {' '.join(f'{key} {value}' for key, value in metadata)}".lower()
    if "feature" in probe or "marker" in probe:
        return "FEATURE_MARKER"
    if "back" in probe and "panel" in probe:
        return "BACK_PANEL"
    if "drawer" in probe:
        return "DRAWER"
    if "door" in probe:
        return "DOOR"
    if "shelf" in probe:
        return "SHELF"
    if "divider" in probe:
        return "DIVIDER"
    if "cabinet" in probe or "carcass" in probe:
        return "CABINET"
    if "panel" in probe or "side" in probe or "top" in probe or "bottom" in probe:
        return "PANEL"
    if "hardware" in probe or "hinge" in probe or "handle" in probe or "slider" in probe:
        return "HARDWARE"
    return "FEATURE_MARKER"


def _state_from_projection(*, visible: bool, selected: bool, highlighted: bool, warnings: tuple[str, ...], representation_status: str) -> str:
    if not visible:
        return "HIDDEN"
    if "unsupported" in representation_status.lower():
        return "UNSUPPORTED"
    if "stale" in representation_status.lower() or any("stale" in warning.lower() for warning in warnings):
        return "STALE"
    if highlighted:
        return "HIGHLIGHTED"
    if selected:
        return "SELECTED"
    return "NORMAL"


def build_visual_components(scene_projection: SceneProjection | None) -> tuple[VisualComponent, ...]:
    if scene_projection is None:
        return ()
    if not isinstance(scene_projection, SceneProjection):
        raise TypeError("scene_projection must be a SceneProjection")

    selected_node_id = scene_projection.selection.selected_node_id
    highlight_target = scene_projection.highlight_target or scene_projection.selection.highlight_target
    representation_status = scene_projection.representation_status or "Unavailable"
    components: list[VisualComponent] = []

    for node in scene_projection.nodes:
        _reject_backend_like_object(node, "scene node projection")
        metadata = tuple(node.display_metadata or ())
        metadata_lookup = _metadata_lookup(metadata)
        component_type = _component_type_from_node_type(node.node_type, metadata)
        component_class = _COMPONENT_CLASS_BY_TYPE[component_type]
        style = _STYLE_BY_TYPE[component_type]
        selected = bool(node.node_id and node.node_id == selected_node_id)
        highlighted = bool(node.node_id and node.node_id == highlight_target)
        warnings = tuple(scene_projection.warnings or ())
        if selected and scene_projection.selection.warnings:
            warnings = warnings + tuple(scene_projection.selection.warnings)
        display_state = _state_from_projection(
            visible=node.visible,
            selected=selected,
            highlighted=highlighted,
            warnings=warnings,
            representation_status=representation_status,
        )
        label = node.display_name or node.node_id
        tooltip_bits = [label, component_type.replace("_", " ").title()]
        material_name = metadata_lookup.get("material", metadata_lookup.get("finish", ""))
        if material_name:
            tooltip_bits.append(material_name)
        components.append(
            component_class(
                id=node.node_id,
                display_name=label,
                color=style["base_color"],
                material_name=material_name,
                visibility=node.visible,
                selection_state="SELECTED" if selected else "NORMAL",
                highlight_state="HIGHLIGHTED" if highlighted else "NORMAL",
                display_state=display_state,
                bounding_box=node.bounding_box,
                display_metadata=metadata + (
                    ("node_type", node.node_type),
                    ("display_state", display_state),
                ),
                warnings=warnings,
                representation_status=representation_status,
                base_color=style["base_color"],
                accent_color=style["accent_color"],
                label=label,
                tooltip=" | ".join(bit for bit in tooltip_bits if bit),
                source_reference=node.source_reference,
            )
        )

    return tuple(components)


__all__ = [
    "VISUAL_COMPONENT_STATES",
    "VisualComponent",
    "CabinetVisualComponent",
    "PanelVisualComponent",
    "DoorVisualComponent",
    "DrawerVisualComponent",
    "ShelfVisualComponent",
    "DividerVisualComponent",
    "BackPanelVisualComponent",
    "HardwareVisualComponent",
    "FeatureMarkerComponent",
    "build_visual_components",
]
