from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .read_models import (
    InspectorFieldReadModel,
    InspectorReadModel,
    MessageCenterReadModel,
    MessageReadModel,
    PreviewItemReadModel,
    PreviewReadModel,
    ProjectTreeNodeReadModel,
    ProjectTreeReadModel,
    ReviewPanelReadModel,
    ReviewSectionReadModel,
    empty_inspector_read_model,
    empty_message_center_read_model,
    empty_preview_read_model,
    empty_project_tree_read_model,
    empty_review_panel_read_models,
)
from .furniture_visual_styles import (
    build_furniture_visual_style,
    style_descriptor_pairs,
)
from .interactive_components import (
    InteractiveVisualComponent,
    interaction_descriptor_pairs,
)
from .scene_projection import (
    SceneNodeProjection,
    SceneProjection,
    build_scene_projection,
)
from .visual_components import VisualComponent, build_visual_components

_SEVERITY_ORDER = {
    "BLOCKER": 5,
    "WARNING": 4,
    "STALE": 3,
    "UNSUPPORTED": 2,
    "INFO": 1,
    "": 0,
}

_SELECTION_NODE_TYPES = {
    "customer": "PROJECT",
    "project": "PROJECT",
    "room": "ROOM",
    "wall": "WALL",
    "product": "PRODUCT",
    "cabinet": "CABINET",
    "document": "DOCUMENT",
    "documents": "DOCUMENT",
}

_REQUIRED_PANEL_NAMES = (
    "Validation",
    "Manufacturing",
    "Cost",
    "Commercial",
    "Release",
)

_INSPECTOR_GROUPS = (
    "Identity",
    "Geometry",
    "Materials",
    "Hardware",
    "Configuration",
    "Manufacturing",
    "Validation",
    "Metadata",
)

_INSPECTOR_METADATA_EXCLUSIONS = {
    "warnings",
    "warning",
    "source_reference",
    "source_region",
    "unsupported",
    "unsupported_reason",
    "suggested_action",
    "stale",
    "fields",
    "selection_id",
    "selection_type",
    "display_name",
}


def _as_dict(source: Any) -> dict[str, Any]:
    if source is None:
        return {}
    if isinstance(source, Mapping):
        return dict(source)
    if hasattr(source, "__dict__"):
        return {
            key: value
            for key, value in vars(source).items()
            if not key.startswith("_")
        }
    return {}


def _get_value(source: Any, key: str, default: Any = None) -> Any:
    if source is None:
        return default
    if isinstance(source, Mapping):
        return source.get(key, default)
    return getattr(source, key, default)


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    return bool(value)


def _string_pairs(source: Any) -> tuple[tuple[str, str], ...]:
    pairs = []
    if source is None:
        return ()
    if isinstance(source, Mapping):
        iterable = source.items()
    else:
        iterable = source
    for item in iterable:
        if isinstance(item, Mapping):
            key = item.get("name", item.get("label", item.get("key", "")))
            value = item.get("value", item.get("text", ""))
        elif isinstance(item, tuple) and len(item) == 2:
            key, value = item
        else:
            key = getattr(item, "name", getattr(item, "label", getattr(item, "key", "")))
            value = getattr(item, "value", getattr(item, "text", ""))
        pairs.append((_as_str(key), _as_str(value)))
    return tuple(pairs)


def _normalize_inspector_group(name: str, label: str, explicit_group: str = "") -> str:
    explicit_group = _as_str(explicit_group).strip()
    if explicit_group:
        return explicit_group
    probe = f"{name} {label}".lower()
    if any(token in probe for token in ("selection_id", "display_name", "selection_type", "source_reference", "id", "name")):
        return "Identity"
    if any(token in probe for token in ("width", "height", "depth", "thickness", "diameter", "angle", "radius", "x", "y", "z", "geometry", "position", "size", "offset")):
        return "Geometry"
    if any(token in probe for token in ("material", "finish", "color", "surface", "veneer", "laminate")):
        return "Materials"
    if any(token in probe for token in ("hardware", "hinge", "slider", "handle", "fastener", "screw", "bolt")):
        return "Hardware"
    if any(token in probe for token in ("manufact", "machin", "edge", "cut", "cnc", "assembly", "drill", "hole")):
        return "Manufacturing"
    if any(token in probe for token in ("warn", "stale", "support", "valid", "block", "error", "tolerance")):
        return "Validation"
    return "Metadata"


def _reject_backend_like_object(value: Any, field_name: str):
    if value is None:
        return
    value_type = type(value)
    module_name = getattr(value_type, "__module__", "")
    if module_name.startswith(("FreeCAD", "Part", "Sketcher")):
        raise TypeError(f"{field_name} cannot contain backend geometry objects")
    if any(hasattr(value, attr) for attr in ("Shape", "ViewObject", "Document")):
        raise TypeError(f"{field_name} cannot contain backend geometry objects")


def _build_project_tree_node(node: Any) -> ProjectTreeNodeReadModel:
    _reject_backend_like_object(node, "project tree node")
    if isinstance(node, (str, int, float, bool)):
        label = _as_str(node)
        return ProjectTreeNodeReadModel(
            node_id=label,
            parent_id="",
            node_type="",
            label=label,
            state="",
            is_supported=True,
            is_stale=False,
            children=(),
        )
    data = _as_dict(node)
    node_type = _as_str(
        _get_value(node, "node_type", _get_value(node, "type", data.get("node_type", "")))
    )
    label = _as_str(_get_value(node, "label", data.get("label", "")))
    if not label:
        label = _as_str(_get_value(node, "name", data.get("name", "")))
    if not node_type:
        node_type = _as_str(_get_value(node, "kind", data.get("kind", "")))
    node_id = _as_str(_get_value(node, "node_id", _get_value(node, "id", label)))
    parent_id = _as_str(_get_value(node, "parent_id", ""))
    state = _as_str(_get_value(node, "state", ""))
    is_supported = _as_bool(_get_value(node, "is_supported", True), True)
    is_stale = _as_bool(_get_value(node, "is_stale", False), False)
    children_source = _get_value(node, "children", ())
    children = tuple(_build_project_tree_node(child) for child in (children_source or ()))
    return ProjectTreeNodeReadModel(
        node_id=node_id,
        parent_id=parent_id,
        node_type=node_type,
        label=label,
        state=state,
        is_supported=is_supported,
        is_stale=is_stale,
        children=children,
    )


def _root_node_from_section(section_name: str, value: Any) -> ProjectTreeNodeReadModel | None:
    if value is None:
        return None
    node_type = _SELECTION_NODE_TYPES.get(section_name.lower(), section_name.upper())
    display_name = section_name.replace("_", " ").title()
    if isinstance(value, (str, int, float, bool)):
        label = _as_str(value)
        node_id = label
        state = ""
        children = ()
    else:
        data = _as_dict(value)
        label = _as_str(data.get("label", data.get("name", display_name)))
        node_id = _as_str(data.get("node_id", data.get("id", section_name.lower())))
        state = _as_str(data.get("state", ""))
        children_source = data.get("children", ()) or ()
        if isinstance(value, (list, tuple)):
            children_source = value
        children = tuple(_build_project_tree_node(child) for child in children_source)
    return ProjectTreeNodeReadModel(
        node_id=node_id,
        parent_id="",
        node_type=node_type,
        label=label,
        state=state,
        is_supported=_as_bool(_get_value(value, "is_supported", True), True),
        is_stale=_as_bool(_get_value(value, "is_stale", False), False),
        children=children,
    )


def build_project_tree_read_model(
    source: Any = None,
    *,
    selected_node_id: str = "",
    expanded_node_ids: Iterable[str] | None = None,
    unsupported_node_ids: Iterable[str] | None = None,
    stale_node_ids: Iterable[str] | None = None,
) -> ProjectTreeReadModel:
    if source is None:
        return empty_project_tree_read_model()
    if isinstance(source, (str, bytes)):
        return empty_project_tree_read_model()

    data = _as_dict(source)
    if "root_nodes" in data:
        root_nodes = tuple(
            _build_project_tree_node(node)
            for node in (data.get("root_nodes", ()) or ())
        )
    else:
        ordered_sections = (
            ("customer", data.get("customer")),
            ("project", data.get("project")),
            ("room", data.get("room")),
            ("wall", data.get("wall")),
            ("product", data.get("product", data.get("cabinet"))),
            ("documents", data.get("documents")),
        )
        root_nodes = tuple(
            node
            for section_name, section_value in ordered_sections
            if (node := _root_node_from_section(section_name, section_value)) is not None
        )
    return ProjectTreeReadModel(
        root_nodes=root_nodes,
        selected_node_id=_as_str(selected_node_id or data.get("selected_node_id", "")),
        expanded_node_ids=tuple(
            _as_str(node_id) for node_id in (expanded_node_ids or data.get("expanded_node_ids", ()) or ())
        ),
        unsupported_node_ids=tuple(
            _as_str(node_id)
            for node_id in (unsupported_node_ids or data.get("unsupported_node_ids", ()) or ())
        ),
        stale_node_ids=tuple(
            _as_str(node_id) for node_id in (stale_node_ids or data.get("stale_node_ids", ()) or ())
        ),
    )


def _build_inspector_field(field: Any) -> InspectorFieldReadModel:
    _reject_backend_like_object(field, "inspector field")
    data = _as_dict(field)
    return InspectorFieldReadModel(
        name=_as_str(_get_value(field, "name", data.get("name", ""))),
        label=_as_str(_get_value(field, "label", _get_value(field, "name", data.get("name", "")))),
        value=_as_str(_get_value(field, "value", _get_value(field, "text", data.get("value", data.get("text", ""))))),
        unit=_as_str(_get_value(field, "unit", data.get("unit", ""))),
        editable=_as_bool(_get_value(field, "editable", data.get("editable", False)), False),
        source_reference=_as_str(_get_value(field, "source_reference", _get_value(field, "source", data.get("source", "")))),
        group=_normalize_inspector_group(
            _as_str(_get_value(field, "name", data.get("name", ""))),
            _as_str(_get_value(field, "label", data.get("label", data.get("name", "")))),
            _as_str(_get_value(field, "group", _get_value(field, "category", data.get("group", data.get("category", ""))))),
        ),
    )


def build_inspector_read_model(
    source: Any = None,
    *,
    selection_id: str | None = None,
    selection_type: str | None = None,
    display_name: str | None = None,
    stale: bool | None = None,
) -> InspectorReadModel:
    if source is None:
        return empty_inspector_read_model()

    data = _as_dict(source)
    metadata_source = _get_value(source, "metadata", data.get("metadata", {}))
    if isinstance(metadata_source, Mapping):
        metadata_source = dict(metadata_source)
    else:
        metadata_source = _as_dict(metadata_source)

    field_source = _get_value(source, "fields", data.get("fields", ()))
    if not field_source and metadata_source:
        field_source = (
            {
                "name": key,
                "label": key.replace("_", " ").title(),
                "value": value,
                "group": "Metadata",
                "source_reference": _get_value(source, "source_region", data.get("source_region", "")),
            }
            for key, value in metadata_source.items()
            if key not in _INSPECTOR_METADATA_EXCLUSIONS
        )
    warnings_source = _get_value(source, "warnings", data.get("warnings", metadata_source.get("warnings", ())))
    if isinstance(warnings_source, str):
        warnings_source = (warnings_source,)
    unsupported = _as_bool(_get_value(source, "unsupported", data.get("unsupported", False)), False)
    unsupported_reason = _as_str(
        _get_value(
            source,
            "unsupported_reason",
            data.get("unsupported_reason", metadata_source.get("unsupported_reason", "")),
        )
    )
    if unsupported_reason and not unsupported:
        unsupported = True
    suggested_action = _as_str(
        _get_value(
            source,
            "suggested_action",
            data.get("suggested_action", metadata_source.get("suggested_action", "")),
        )
    )
    source_reference = _as_str(
        _get_value(
            source,
            "source_reference",
            _get_value(source, "source_region", data.get("source_reference", data.get("source_region", ""))),
        )
    )
    if not source_reference and metadata_source.get("source_reference"):
        source_reference = _as_str(metadata_source.get("source_reference", ""))
    resolved_selection_id = _as_str(
        selection_id
        if selection_id is not None
        else data.get("selection_id", data.get("id", data.get("node_id", "")))
    )
    resolved_display_name = _as_str(
        display_name
        if display_name is not None
        else data.get("display_name", data.get("label", data.get("name", "")))
    )
    if not resolved_display_name:
        resolved_display_name = resolved_selection_id

    return InspectorReadModel(
        selection_id=resolved_selection_id,
        selection_type=_as_str(
            selection_type if selection_type is not None else data.get("selection_type", data.get("node_type", "NONE"))
        ),
        display_name=resolved_display_name,
        fields=tuple(_build_inspector_field(field) for field in (field_source or ())),
        warnings=tuple(_as_str(warning) for warning in (warnings_source or ())),
        source_reference=source_reference,
        unsupported=unsupported,
        unsupported_reason=unsupported_reason,
        suggested_action=suggested_action,
        stale=_as_bool(stale if stale is not None else data.get("stale", False), False),
    )


def _build_preview_item(item: Any) -> PreviewItemReadModel:
    _reject_backend_like_object(item, "preview item")
    data = _as_dict(item)
    item_type = _as_str(_get_value(item, "item_type", data.get("item_type", data.get("type", ""))))
    if not item_type:
        item_type = _as_str(_get_value(item, "node_type", data.get("node_type", "")))
    display_metadata = _get_value(item, "display_metadata", data.get("display_metadata", ()))
    return PreviewItemReadModel(
        item_id=_as_str(_get_value(item, "item_id", _get_value(item, "id", data.get("item_id", "")))),
        item_type=item_type,
        label=_as_str(_get_value(item, "label", data.get("label", ""))),
        visible=_as_bool(_get_value(item, "visible", True), True),
        selected=_as_bool(_get_value(item, "selected", False), False),
        display_metadata=_string_pairs(display_metadata),
        source_reference=_as_str(_get_value(item, "source_reference", _get_value(item, "source", ""))),
        representation=_as_str(_get_value(item, "representation", data.get("representation", ""))),
    )


def _build_preview_item_from_selection(selection: Any, *, representation: str = "") -> PreviewItemReadModel:
    _reject_backend_like_object(selection, "preview selection")
    data = _as_dict(selection)
    metadata = _get_value(selection, "metadata", data.get("metadata", {}))
    if isinstance(metadata, Mapping):
        metadata = dict(metadata)
    else:
        metadata = _as_dict(metadata)
    display_metadata = tuple(
        (key, _as_str(value))
        for key, value in metadata.items()
        if key not in {"warnings", "unsupported_reason", "suggested_action"}
    )
    item_id = _as_str(
        _get_value(selection, "selection_id", data.get("selection_id", data.get("id", data.get("node_id", ""))))
    )
    item_type = _as_str(
        _get_value(selection, "selection_type", data.get("selection_type", data.get("node_type", "NONE")))
    )
    label = _as_str(
        _get_value(selection, "display_name", data.get("display_name", data.get("label", data.get("name", ""))))
    )
    if not label:
        label = item_id
    return PreviewItemReadModel(
        item_id=item_id,
        item_type=item_type,
        label=label,
        visible=True,
        selected=True,
        display_metadata=display_metadata,
        source_reference=_as_str(_get_value(selection, "source_region", data.get("source_region", ""))),
        representation=representation,
    )


def _build_preview_item_from_scene_node(
    node: SceneNodeProjection,
    *,
    selected_node_id: str = "",
    highlight_target: str = "",
    representation: str = "Scene Projection",
) -> PreviewItemReadModel:
    selected = bool(
        node.node_id
        and node.node_id
        in {
            _as_str(selected_node_id),
            _as_str(highlight_target),
        }
    )
    metadata = node.display_metadata + (
        ("visible", str(node.visible)),
        ("selectable", str(node.selectable)),
    )
    return PreviewItemReadModel(
        item_id=node.node_id,
        item_type=node.node_type or "SCENE_NODE",
        label=node.display_name or node.node_id,
        visible=node.visible,
        selected=selected,
        display_metadata=metadata,
        source_reference=node.source_reference,
        representation=representation,
    )


def _build_preview_item_from_visual_component(component: VisualComponent) -> PreviewItemReadModel:
    _reject_backend_like_object(component, "visual component")
    style = build_furniture_visual_style(component)
    style_pairs = style_descriptor_pairs(style)
    metadata = component.display_metadata + (
        ("material", component.material_name),
        ("base_color", component.base_color),
        ("accent_color", component.accent_color),
        ("icon_name", component.icon_name),
        ("future_theme_key", component.future_theme_key),
        ("selection_state", component.selection_state),
        ("highlight_state", component.highlight_state),
        ("display_state", component.display_state),
    ) + style_pairs
    return PreviewItemReadModel(
        item_id=component.id,
        item_type=component.component_type,
        label=component.label or component.display_name or component.id,
        visible=component.visibility,
        selected=component.selection_state == "SELECTED" or component.highlight_state == "HIGHLIGHTED",
        display_metadata=tuple((key, value) for key, value in metadata if value != ""),
        source_reference=component.source_reference,
        representation=component.representation_status,
    )


def _build_preview_item_from_interactive_component(
    interactive: InteractiveVisualComponent,
) -> PreviewItemReadModel:
    _reject_backend_like_object(interactive, "interactive component")
    interaction = interactive.interaction
    vis = interaction.visibility
    overlay = interaction.overlay
    motion = interaction.motion

    metadata = (
        ("component_id", interactive.component_id),
        ("component_type", interactive.component_type),
        ("interaction_state", interaction.state_label),
        ("selected", "yes" if overlay.selected else "no"),
        ("highlighted", "yes" if overlay.highlighted else "no"),
        ("expanded", "yes" if overlay.expanded else "no"),
        ("visible", "yes" if vis.visible else "no"),
        ("hardware_visible", "yes" if vis.hardware_visible else "no"),
        ("feature_markers_visible", "yes" if vis.feature_markers_visible else "no"),
        ("door_swing_visible", "yes" if vis.door_swing_visible else "no"),
        ("drawer_open_visible", "yes" if vis.drawer_open_visible else "no"),
    )
    if motion.motion_hint:
        metadata = metadata + (("motion_hint", motion.motion_hint),)
    filtered = tuple(
        (k, v) for k, v in metadata if v not in ("", "no")
    )
    return PreviewItemReadModel(
        item_id=interactive.component_id,
        item_type=interactive.component_type or "",
        label=interactive.display_name or interactive.component_id,
        visible=vis.visible,
        selected=overlay.selected,
        display_metadata=filtered,
        source_reference=interaction.source_reference,
        representation=interaction.state_label,
    )


def _resolve_scene_projection(source: Any, data: dict[str, Any]) -> SceneProjection | None:
    scene_projection = _get_value(source, "scene_projection", data.get("scene_projection", None))
    if isinstance(scene_projection, SceneProjection):
        return scene_projection
    if scene_projection is not None:
        return build_scene_projection(
            scene_projection,
            selected_node_id=_as_str(_get_value(source, "selected_node_id", data.get("selected_node_id", ""))),
            highlight_target=_as_str(_get_value(source, "highlight_target", data.get("highlight_target", ""))),
            representation_status=_as_str(
                _get_value(source, "representation_status", data.get("representation_status", ""))
            ),
            warnings=_get_value(source, "warnings", data.get("warnings", ())),
            source_reference=_as_str(_get_value(source, "source_reference", data.get("source_reference", ""))),
        )
    if isinstance(source, SceneProjection):
        return source
    if isinstance(source, Mapping) and "scene_graph" in source:
        return build_scene_projection(
            source.get("scene_graph"),
            selected_node_id=_as_str(_get_value(source, "selected_node_id", data.get("selected_node_id", ""))),
            highlight_target=_as_str(_get_value(source, "highlight_target", data.get("highlight_target", ""))),
            representation_status=_as_str(
                _get_value(source, "representation_status", data.get("representation_status", ""))
            ),
            warnings=_get_value(source, "warnings", data.get("warnings", ())),
            source_reference=_as_str(_get_value(source, "source_reference", data.get("source_reference", ""))),
        )
    if hasattr(source, "all_nodes") and callable(getattr(source, "all_nodes")):
        return build_scene_projection(
            source,
            selected_node_id=_as_str(_get_value(source, "selected_node_id", data.get("selected_node_id", ""))),
            highlight_target=_as_str(_get_value(source, "highlight_target", data.get("highlight_target", ""))),
            representation_status=_as_str(
                _get_value(source, "representation_status", data.get("representation_status", ""))
            ),
            warnings=_get_value(source, "warnings", data.get("warnings", ())),
            source_reference=_as_str(_get_value(source, "source_reference", data.get("source_reference", ""))),
        )
    if hasattr(source, "nodes") and not isinstance(source, (str, bytes)):
        return build_scene_projection(
            source,
            selected_node_id=_as_str(_get_value(source, "selected_node_id", data.get("selected_node_id", ""))),
            highlight_target=_as_str(_get_value(source, "highlight_target", data.get("highlight_target", ""))),
            representation_status=_as_str(
                _get_value(source, "representation_status", data.get("representation_status", ""))
            ),
            warnings=_get_value(source, "warnings", data.get("warnings", ())),
            source_reference=_as_str(_get_value(source, "source_reference", data.get("source_reference", ""))),
        )
    return None


def _resolve_visual_components(source: Any, data: dict[str, Any]) -> tuple[VisualComponent, ...]:
    visual_components = _get_value(source, "visual_components", data.get("visual_components", ()))
    if visual_components:
        components = tuple(visual_components or ())
        for component in components:
            if not isinstance(component, VisualComponent):
                raise TypeError("visual_components must contain VisualComponent instances")
        return components
    scene_projection = _resolve_scene_projection(source, data)
    if scene_projection is not None:
        return build_visual_components(scene_projection)
    return ()


def _resolve_interactive_components(
    source: Any, data: dict[str, Any]
) -> tuple[InteractiveVisualComponent, ...] | None:
    interactive = _get_value(source, "interactive_components", data.get("interactive_components", None))
    if interactive is not None:
        result = tuple(interactive or ())
        for ic in result:
            if not isinstance(ic, InteractiveVisualComponent):
                raise TypeError("interactive_components must contain InteractiveVisualComponent instances")
        return result
    return None


def _visual_component_bounds_label(components: tuple[VisualComponent, ...]) -> str:
    if not components:
        return ""
    min_x = min(component.bounding_box.minimum[0] for component in components)
    min_y = min(component.bounding_box.minimum[1] for component in components)
    min_z = min(component.bounding_box.minimum[2] for component in components)
    max_x = max(component.bounding_box.maximum[0] for component in components)
    max_y = max(component.bounding_box.maximum[1] for component in components)
    max_z = max(component.bounding_box.maximum[2] for component in components)
    return f"min=({min_x}, {min_y}, {min_z}) max=({max_x}, {max_y}, {max_z})"


def build_selection_preview_source(
    *,
    selection: Any = None,
    scene_graph: Any = None,
    current_family: str = "",
    current_product: str = "",
    active_family: str = "",
) -> dict[str, Any]:
    selection = selection or {}
    selection_id = _as_str(_get_value(selection, "selection_id", ""))
    selection_type = _as_str(_get_value(selection, "selection_type", ""))
    display_name = _as_str(_get_value(selection, "display_name", ""))
    has_selection = selection_type not in ("", "NONE")

    if scene_graph is not None:
        return {
            "scene_graph": scene_graph,
            "selection": selection,
            "selected_node_id": selection_id if has_selection else "",
            "highlight_target": selection_id if has_selection else "",
            "current_family": current_family or active_family,
            "preview_title": current_product or current_family or display_name or "Engineering Preview",
            "preview_state": "Ready",
            "viewport_message": (
                f"Focus on {display_name or selection_id}"
                if has_selection else
                "Current engineering model ready"
            ),
            "available_representations": (
                "Customer View",
                "Design View",
            ),
            "representation_status": "Ready",
            "warnings": (),
        }

    return {
        "selection": selection,
        "current_family": current_family,
        "preview_title": current_family or display_name or "Preview",
        "preview_state": "Ready" if has_selection else "Unavailable",
        "viewport_message": (
            f"Focus on {display_name or selection_id or 'current selection'}"
            if has_selection
            else "Select a project or product to populate preview"
        ),
        "available_representations": (
            ("Customer View", "Design View")
            if has_selection
            else ()
        ),
        "highlight_representation": "Selection Focus" if has_selection else "",
        "warnings": (),
    }


def build_preview_read_model(
    source: Any = None,
    *,
    preview_mode: str | None = None,
    highlighted_item_id: str | None = None,
    stale: bool | None = None,
    unsupported_reason: str | None = None,
) -> PreviewReadModel:
    if source is None:
        return empty_preview_read_model()
    _reject_backend_like_object(source, "preview source")
    data = _as_dict(source)
    scene_projection = _resolve_scene_projection(source, data)
    visual_components = _resolve_visual_components(source, data)
    interactive_components = _resolve_interactive_components(source, data)
    selection_source = _get_value(source, "selection", data.get("selection", None))
    items_source = _get_value(source, "items", data.get("items", ()))
    available_representations = _get_value(
        source,
        "available_representations",
        data.get("available_representations", ()),
    )
    if isinstance(available_representations, str):
        available_representations = (available_representations,)
    viewport_message = _as_str(_get_value(source, "viewport_message", data.get("viewport_message", "")))
    preview_title = _as_str(
        _get_value(source, "preview_title", data.get("preview_title", data.get("title", "")))
    )
    current_family = _as_str(
        _get_value(source, "current_family", data.get("current_family", data.get("product_family", "")))
    )
    preview_state = _as_str(_get_value(source, "preview_state", data.get("preview_state", "Unavailable")))
    warnings_source = _get_value(source, "warnings", data.get("warnings", ()))
    if isinstance(warnings_source, str):
        warnings_source = (warnings_source,)
    scene_items: tuple[PreviewItemReadModel, ...] = ()
    scene_available = False
    scene_bounds = ""
    node_count = 0
    selected_node = ""
    highlight_target = _as_str(_get_value(source, "highlight_target", data.get("highlight_target", "")))
    representation_status = _as_str(
        _get_value(source, "representation_status", data.get("representation_status", "Unavailable"))
    )
    selection_item = None

    if scene_projection is not None:
        if interactive_components is not None:
            scene_items = tuple(
                _build_preview_item_from_interactive_component(ic)
                for ic in interactive_components
            )
        elif visual_components:
            scene_items = tuple(
                _build_preview_item_from_visual_component(component)
                for component in visual_components
            )
            highlighted_component = next(
                (
                    component
                    for component in visual_components
                    if component.highlight_state == "HIGHLIGHTED" or component.selection_state == "SELECTED"
                ),
                None,
            )
            if highlighted_component is not None and not data.get("highlighted_item_type"):
                data["highlighted_item_type"] = highlighted_component.component_type
        else:
            scene_items = tuple(
                _build_preview_item_from_scene_node(
                    node,
                    selected_node_id=scene_projection.selection.selected_node_id,
                    highlight_target=scene_projection.highlight_target,
                    representation=scene_projection.representation_status or "Scene Projection",
                )
                for node in scene_projection.nodes
            )
        scene_available = scene_projection.scene_available
        scene_bounds = scene_projection.bounds.display_label
        node_count = len(visual_components) or scene_projection.node_count or len(scene_projection.nodes)
        selected_node = scene_projection.selection.selected_node_id
        highlight_target = scene_projection.highlight_target or scene_projection.selection.highlight_target
        representation_status = scene_projection.representation_status or representation_status
        warnings_source = scene_projection.warnings or warnings_source
        if not preview_title:
            preview_title = scene_projection.selection.display_name or _as_str(data.get("preview_title", ""))
        if not current_family:
            current_family = _as_str(data.get("current_family", ""))
        if not preview_state or preview_state == "Unavailable":
            preview_state = "Ready" if scene_available else "Unavailable"
        if not viewport_message:
            viewport_message = (
                scene_projection.selection.display_name
                or scene_projection.highlight_target
                or "Scene projection ready"
            )
        if not available_representations:
            available_representations = ("Customer View", "Design View") if scene_available else ()
        items_source = scene_items
        selection_source = scene_projection.selection if scene_projection.selection.selected_node_id else selection_source
        highlighted_item_id = highlighted_item_id or scene_projection.selection.selected_node_id or scene_projection.highlight_target
    elif visual_components or interactive_components is not None:
        if interactive_components is not None:
            scene_items = tuple(
                _build_preview_item_from_interactive_component(ic)
                for ic in interactive_components
            )
            scene_available = any(
                ic.interaction.visibility.visible for ic in interactive_components
            )
            node_count = len(interactive_components)
            selected_interactive = next(
                (ic for ic in interactive_components if ic.interaction.overlay.selected),
                None,
            )
            selected_node = _as_str(
                highlighted_item_id
                or (selected_interactive.component_id if selected_interactive is not None else "")
                or data.get("selected_node", data.get("selected_node_id", ""))
            )
            highlighted_item_id = _as_str(
                highlighted_item_id
                or (selected_interactive.component_id if selected_interactive is not None else "")
                or data.get("highlighted_item_id", "")
            )
            if selected_interactive is not None and not data.get("highlighted_item_type"):
                data["highlighted_item_type"] = selected_interactive.component_type
            if not preview_title:
                preview_title = _as_str(
                    data.get(
                        "preview_title",
                        selected_interactive.display_name if selected_interactive is not None else "Preview",
                    )
                )
            if not preview_state or preview_state == "Unavailable":
                preview_state = "Ready" if scene_items else "Unavailable"
            if not viewport_message:
                viewport_message = (
                    f"Preview focus: {selected_interactive.display_name}"
                    if selected_interactive is not None
                    else "Interactive components ready"
                )
            if not available_representations:
                available_representations = tuple(
                    ic.interaction.state_label or ic.component_type
                    for ic in interactive_components
                    if ic.interaction.visibility.visible
                )
            if not warnings_source:
                warnings_source = tuple(
                    w
                    for ic in interactive_components
                    for w in ic.interaction.warnings
                )
        else:
            scene_items = tuple(
                _build_preview_item_from_visual_component(component)
                for component in visual_components
            )
            scene_available = any(component.visibility for component in visual_components)
            scene_bounds = _visual_component_bounds_label(visual_components)
            node_count = len(visual_components)
            selected_component = next(
                (
                    component
                    for component in visual_components
                    if component.selection_state == "SELECTED" or component.highlight_state == "HIGHLIGHTED"
                ),
                None,
            )
            selected_node = _as_str(
                highlighted_item_id
                or (selected_component.id if selected_component is not None else "")
                or data.get("selected_node", data.get("selected_node_id", ""))
            )
            highlighted_item_id = _as_str(
                highlighted_item_id
                or (selected_component.id if selected_component is not None else "")
                or data.get("highlighted_item_id", "")
            )
            if selected_component is not None and not data.get("highlighted_item_type"):
                data["highlighted_item_type"] = selected_component.component_type
            if not preview_title:
                preview_title = _as_str(
                    data.get(
                        "preview_title",
                        selected_component.label if selected_component is not None else "Preview",
                    )
                )
            if not preview_state or preview_state == "Unavailable":
                preview_state = "Ready" if scene_items else "Unavailable"
            if not viewport_message:
                viewport_message = (
                    f"Preview focus: {selected_component.label}"
                    if selected_component is not None
                    else "Visual components ready"
                )
            if not available_representations:
                available_representations = tuple(
                    component.representation_status or component.component_type
                    for component in visual_components
                    if component.visibility
                )
            if not warnings_source:
                warnings_source = tuple(
                    warning
                    for component in visual_components
                    for warning in component.warnings
                )
        if not current_family:
            current_family = _as_str(data.get("current_family", ""))
        highlight_target = _as_str(data.get("highlight_target", highlighted_item_id or ""))
        representation_status = _as_str(
            _get_value(source, "representation_status", data.get("representation_status", "Ready"))
        )
    else:
        selection_type_value = _as_str(
            _get_value(selection_source, "selection_type", data.get("highlighted_item_type", data.get("selection_type", "NONE")))
        )
        selection_id_value = _as_str(
            _get_value(selection_source, "selection_id", data.get("highlighted_item_id", data.get("selection_id", "")))
        )
        selection_label_value = _as_str(
            _get_value(selection_source, "display_name", data.get("display_name", data.get("highlighted_item_label", "")))
        )
        if selection_source is not None and not items_source and (
            selection_type_value not in ("", "NONE") or selection_id_value or selection_label_value
        ):
            items_source = (selection_source,)
        if selection_source is not None and (
            selection_type_value not in ("", "NONE") or selection_id_value or selection_label_value
        ):
            selection_item = _build_preview_item_from_selection(
                selection_source,
                representation=_as_str(_get_value(source, "highlight_representation", data.get("highlight_representation", ""))),
            )
        elif highlighted_item_id:
            selection_item = PreviewItemReadModel(
                item_id=_as_str(highlighted_item_id),
                item_type=_as_str(data.get("highlighted_item_type", "")),
                label=_as_str(data.get("highlighted_item_label", highlighted_item_id)),
                visible=True,
                selected=True,
                display_metadata=(),
                source_reference=_as_str(data.get("source_reference", "")),
                representation=_as_str(data.get("highlight_representation", "")),
            )
        if selection_item is not None:
            if not highlighted_item_id:
                highlighted_item_id = selection_item.item_id
            if not data.get("highlighted_item_type"):
                data["highlighted_item_type"] = selection_item.item_type
            if not preview_title:
                preview_title = selection_item.label or selection_item.item_id
        has_preview_content = bool(items_source) or selection_item is not None
        if not preview_state or preview_state == "Unavailable":
            preview_state = "Ready" if has_preview_content else "Unavailable"
        if not viewport_message:
            if selection_item is not None:
                viewport_message = f"Preview focus: {selection_item.label or selection_item.item_id}"
            elif highlighted_item_id:
                viewport_message = f"Preview focus: {highlighted_item_id}"
            else:
                viewport_message = "Preview unavailable"
        if not current_family:
            current_family = _as_str(data.get("current_family", ""))
        item_models = tuple(_build_preview_item(item) for item in (items_source or ()))
        if selection_item is not None and not any(item.item_id == selection_item.item_id for item in item_models):
            item_models = (selection_item,) + item_models
        if not available_representations:
            if item_models:
                available_representations = tuple(
                    _as_str(item.representation or item.item_type or "Default") for item in item_models if item.visible
                )
            elif selection_item is not None:
                available_representations = (
                    _as_str(selection_item.representation or selection_item.item_type or "Default"),
                )
        scene_available = bool(item_models)
        node_count = len(item_models)
        selected_node = _as_str(highlighted_item_id or data.get("selected_node", data.get("selected_node_id", "")))
        scene_bounds = _as_str(data.get("scene_bounds", ""))
        highlight_target = _as_str(data.get("highlight_target", highlighted_item_id or ""))
        representation_status = _as_str(
            _get_value(source, "representation_status", data.get("representation_status", "Unavailable"))
        )
        scene_items = item_models

    return PreviewReadModel(
        preview_title=preview_title or "Preview",
        preview_mode=_as_str(preview_mode if preview_mode is not None else data.get("preview_mode", "Customer View")),
        preview_state=preview_state,
        items=scene_items,
        scene_available=scene_available,
        scene_bounds=scene_bounds,
        node_count=node_count,
        selected_node=selected_node,
        highlighted_item_id=_as_str(highlighted_item_id if highlighted_item_id is not None else data.get("highlighted_item_id", "")),
        highlighted_item_type=_as_str(
            data.get(
                "highlighted_item_type",
                scene_projection.selection.node_type if scene_projection is not None else (
                    selection_item.item_type if selection_item is not None else ""
                ),
            )
        ),
        highlight_target=_as_str(highlight_target or highlighted_item_id or data.get("highlight_target", "")),
        current_family=current_family,
        viewport_message=viewport_message or _as_str(data.get("viewport_message", "")),
        representation_status=representation_status,
        available_representations=tuple(_as_str(item) for item in (available_representations or ())),
        warnings=tuple(_as_str(warning) for warning in (warnings_source or ())),
        stale=_as_bool(stale if stale is not None else data.get("stale", False), False),
        unsupported_reason=_as_str(unsupported_reason if unsupported_reason is not None else data.get("unsupported_reason", "")),
    )


def _build_message(message: Any) -> MessageReadModel:
    _reject_backend_like_object(message, "message")
    data = _as_dict(message)
    severity = _as_str(_get_value(message, "severity", data.get("severity", "INFO"))).upper() or "INFO"
    blocking_value = _get_value(message, "blocking", None)
    return MessageReadModel(
        message_id=_as_str(_get_value(message, "message_id", _get_value(message, "id", data.get("id", "")))),
        severity=severity,
        category=_as_str(_get_value(message, "category", data.get("category", ""))),
        text=_as_str(_get_value(message, "text", data.get("text", ""))),
        source_reference=_as_str(_get_value(message, "source_reference", _get_value(message, "source", ""))),
        acknowledged=_as_bool(_get_value(message, "acknowledged", data.get("acknowledged", False)), False),
        blocking=_as_bool(blocking_value if blocking_value is not None else severity == "BLOCKER", severity == "BLOCKER"),
    )


def build_message_center_read_model(
    source: Any = None,
    *,
    messages: Iterable[Any] | None = None,
) -> MessageCenterReadModel:
    if source is None and messages is None:
        return empty_message_center_read_model()
    data = _as_dict(source)
    message_source = messages if messages is not None else _get_value(source, "messages", data.get("messages", ()))
    message_models = tuple(_build_message(message) for message in (message_source or ()))
    highest_severity = "INFO"
    highest_rank = _SEVERITY_ORDER[highest_severity]
    has_blockers = False
    has_stale_outputs = False
    for message in message_models:
        rank = _SEVERITY_ORDER.get(message.severity, 0)
        if rank > highest_rank:
            highest_rank = rank
            highest_severity = message.severity
        has_blockers = has_blockers or message.blocking
        has_stale_outputs = has_stale_outputs or message.severity == "STALE"
    return MessageCenterReadModel(
        messages=message_models,
        highest_severity=highest_severity,
        has_blockers=has_blockers,
        has_stale_outputs=has_stale_outputs,
    )


def _build_review_section(section: Any) -> ReviewSectionReadModel:
    _reject_backend_like_object(section, "review section")
    data = _as_dict(section)
    return ReviewSectionReadModel(
        section_name=_as_str(_get_value(section, "section_name", data.get("section_name", ""))),
        rows=_string_pairs(_get_value(section, "rows", data.get("rows", ()))),
        warnings=tuple(_as_str(warning) for warning in (_get_value(section, "warnings", data.get("warnings", ())) or ())),
        source_reference=_as_str(_get_value(section, "source_reference", _get_value(section, "source", ""))),
    )


def build_review_panel_read_models(
    source: Any = None,
    *,
    panel_names: tuple[str, ...] = _REQUIRED_PANEL_NAMES,
) -> tuple[ReviewPanelReadModel, ...]:
    if source is None:
        return empty_review_panel_read_models(panel_names)
    data = _as_dict(source)
    panels_source = _get_value(source, "panels", data.get("panels", {}))
    if isinstance(panels_source, Mapping):
        panel_map = dict(panels_source)
    else:
        panel_map = {}
        for panel in (panels_source or ()):
            panel_data = _as_dict(panel)
            panel_name = _as_str(panel_data.get("panel_name", panel_data.get("name", "")))
            if panel_name:
                panel_map[panel_name] = panel
    results = []
    for panel_name in panel_names:
        panel_source = panel_map.get(panel_name)
        if panel_source is None:
            results.append(ReviewPanelReadModel(panel_name=panel_name))
            continue
        panel_data = _as_dict(panel_source)
        sections_source = _get_value(panel_source, "sections", panel_data.get("sections", ()))
        results.append(
            ReviewPanelReadModel(
                panel_name=panel_name,
                sections=tuple(_build_review_section(section) for section in (sections_source or ())),
                stale=_as_bool(_get_value(panel_source, "stale", panel_data.get("stale", False)), False),
                available=_as_bool(_get_value(panel_source, "available", panel_data.get("available", True)), True),
            )
        )
    return tuple(results)


def _mfg_op_label(op: Any, data: dict[str, Any]) -> str:
    """Extract a safe display label from a manufacturing operation object."""
    label = _as_str(
        _get_value(
            op, "operation_label",
            _get_value(
                op, "label",
                _get_value(
                    op, "operation",
                    data.get("operation_label",
                             data.get("label",
                                      data.get("operation", ""))),
                ),
            ),
        )
    )
    name = _as_str(
        _get_value(
            op, "operation_name",
            _get_value(
                op, "name",
                data.get("operation_name",
                         data.get("name", "")),
            ),
        )
    )
    return label or name


def _mfg_op_status(op: Any, data: dict[str, Any]) -> str:
    """Extract a safe status string from a manufacturing operation."""
    status = _as_str(
        _get_value(op, "operation_status",
        _get_value(op, "status",
        data.get("operation_status",
        data.get("status", "")))))
    return status.upper() if status else "UNKNOWN"


def _mfg_op_detail(op: Any, data: dict[str, Any]) -> str:
    """Extract a safe detail/message string from a manufacturing operation."""
    return _as_str(
        _get_value(op, "operation_message",
        _get_value(op, "message",
        _get_value(op, "detail",
        data.get("operation_message",
        data.get("message",
        data.get("detail", "")))))))


def build_manufacturing_review_projection(
    source: Any = None,
) -> ReviewPanelReadModel:
    """Project duck-typed manufacturing source into a ReviewPanelReadModel.

    Accepts:
    - An object with ``operations`` attribute (iterable of operation objects)
    - A dict with ``"operations"`` key
    - A list/tuple of operation objects directly

    Each operation object may expose (via attribute or dict key):
    - ``operation_label`` / ``label`` / ``operation`` / ``name`` — display label
    - ``operation_status`` / ``status`` — e.g. PASS, FAIL, WARNING, SKIPPED
    - ``operation_message`` / ``message`` / ``detail`` — detail text
    - ``component_id`` — optional linked component ID

    Operations are grouped into sections by status category.

    Returns a ReviewPanelReadModel with panel_name="Manufacturing".
    No raw manufacturing objects leak into the output.
    """
    _reject_backend_like_object(source, "manufacturing source")

    if source is None:
        return ReviewPanelReadModel(
            panel_name="Manufacturing",
            available=False,
        )

    # ── Extract raw operations ─────────────────────────────────────
    data = _as_dict(source)
    raw_ops = _get_value(source, "operations", data.get("operations", None))

    if raw_ops is None:
        # Source might be a list/tuple of operations directly
        if isinstance(source, (list, tuple)):
            raw_ops = source
        elif hasattr(source, "__iter__") and not isinstance(source, (str, bytes, Mapping)):
            raw_ops = list(source)
        else:
            raw_ops = ()

    if not raw_ops:
        return ReviewPanelReadModel(
            panel_name="Manufacturing",
            sections=(
                ReviewSectionReadModel(
                    section_name="Manufacturing Operations",
                    rows=(("Status", "No operations data"),),
                    warnings=("Manufacturing data not available",),
                ),
            ),
            available=False,
        )

    # ── Convert each operation to a row ────────────────────────────
    passed_rows: list[tuple[str, str]] = []
    failed_rows: list[tuple[str, str]] = []
    warning_rows: list[tuple[str, str]] = []
    skipped_rows: list[tuple[str, str]] = []
    other_rows: list[tuple[str, str]] = []
    all_warnings: list[str] = []

    for op in raw_ops:
        _reject_backend_like_object(op, "manufacturing operation")
        op_data = _as_dict(op)

        label = _mfg_op_label(op, op_data)
        status = _mfg_op_status(op, op_data)
        detail = _mfg_op_detail(op, op_data)
        cid = _as_str(
            _get_value(op, "component_id",
            _get_value(op, "cid",
            op_data.get("component_id",
            op_data.get("cid", "")))))

        # Build the value part of the row
        value_parts = [status]
        if detail:
            value_parts.append(detail)
        if cid:
            value_parts.append(f"[{cid}]")
        value = " | ".join(value_parts)

        row = (label, value)

        if status == "PASS":
            passed_rows.append(row)
        elif status == "FAIL":
            failed_rows.append(row)
            all_warnings.append(f"{label}: {detail or 'Failed'}")
        elif status == "WARNING":
            warning_rows.append(row)
            all_warnings.append(f"{label}: {detail or 'Warning'}")
        elif status == "SKIPPED":
            skipped_rows.append(row)
        else:
            other_rows.append(row)

    # ── Build sections ─────────────────────────────────────────────
    sections: list[ReviewSectionReadModel] = []

    if failed_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Failed",
                rows=tuple(failed_rows),
                warnings=tuple(w for w in all_warnings if "Failed" in w),
            )
        )
    if warning_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Warnings",
                rows=tuple(warning_rows),
                warnings=tuple(w for w in all_warnings if "Warning" in w),
            )
        )
    if passed_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Passed",
                rows=tuple(passed_rows),
            )
        )
    if skipped_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Skipped",
                rows=tuple(skipped_rows),
            )
        )
    if other_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Other",
                rows=tuple(other_rows),
            )
        )

    return ReviewPanelReadModel(
        panel_name="Manufacturing",
        sections=tuple(sections),
        available=True,
    )


def _val_rule_label(violation: Any, data: dict[str, Any]) -> str:
    """Extract a safe display label from a validation violation object."""
    label = _as_str(
        _get_value(
            violation, "rule_label",
            _get_value(
                violation, "label",
                _get_value(
                    violation, "rule",
                    data.get("rule_label",
                             data.get("label",
                                      data.get("rule", ""))),
                ),
            ),
        )
    )
    name = _as_str(
        _get_value(
            violation, "rule_name",
            _get_value(
                violation, "name",
                data.get("rule_name",
                         data.get("name", "")),
            ),
        )
    )
    return label or name


def _val_severity(violation: Any, data: dict[str, Any]) -> str:
    """Extract a safe severity string from a validation violation."""
    severity = _as_str(
        _get_value(violation, "violation_severity",
        _get_value(violation, "severity",
        data.get("violation_severity",
        data.get("severity", "")))))
    return severity.upper() if severity else "INFO"


def _val_status(violation: Any, data: dict[str, Any]) -> str:
    """Extract a safe status string from a validation violation."""
    status = _as_str(
        _get_value(violation, "violation_status",
        _get_value(violation, "status",
        data.get("violation_status",
        data.get("status", "")))))
    return status.upper() if status else "UNKNOWN"


def _val_message(violation: Any, data: dict[str, Any]) -> str:
    """Extract a safe message string from a validation violation."""
    return _as_str(
        _get_value(violation, "violation_message",
        _get_value(violation, "message",
        _get_value(violation, "detail",
        data.get("violation_message",
        data.get("message",
        data.get("detail", "")))))))


def build_validation_review_projection(
    source: Any = None,
) -> ReviewPanelReadModel:
    """Project duck-typed validation source into a ReviewPanelReadModel.

    Accepts:
    - An object with ``violations`` attribute (iterable of violation objects)
    - A dict with ``\"violations\"`` key
    - A list/tuple of violation objects directly

    Each violation object may expose (via attribute or dict key):
    - ``rule_label`` / ``label`` / ``rule`` / ``name`` — display label
    - ``violation_severity`` / ``severity`` — e.g. ERROR, WARNING, INFO
    - ``violation_status`` / ``status`` — e.g. PASS, FAIL
    - ``violation_message`` / ``message`` / ``detail`` — detail text
    - ``component_id`` — optional linked component ID

    Results are grouped into sections: Errors, Warnings, Passed, Info, Other.

    Returns a ReviewPanelReadModel with panel_name=\"Validation\".
    No raw validation objects leak into the output.
    """
    _reject_backend_like_object(source, "validation source")

    if source is None:
        return ReviewPanelReadModel(
            panel_name="Validation",
            available=False,
        )

    # ── Extract raw violations ─────────────────────────────────────
    data = _as_dict(source)
    raw_violations = _get_value(source, "violations", data.get("violations", None))

    if raw_violations is None:
        if isinstance(source, (list, tuple)):
            raw_violations = source
        elif hasattr(source, "__iter__") and not isinstance(source, (str, bytes, Mapping)):
            raw_violations = list(source)
        else:
            raw_violations = ()

    if not raw_violations:
        return ReviewPanelReadModel(
            panel_name="Validation",
            sections=(
                ReviewSectionReadModel(
                    section_name="Validation Rules",
                    rows=(("Status", "No validation data"),),
                    warnings=("Validation data not available",),
                ),
            ),
            available=False,
        )

    # ── Convert each violation to a row ────────────────────────────
    error_rows: list[tuple[str, str]] = []
    warning_rows: list[tuple[str, str]] = []
    passed_rows: list[tuple[str, str]] = []
    info_rows: list[tuple[str, str]] = []
    other_rows: list[tuple[str, str]] = []
    all_warnings: list[str] = []

    for violation in raw_violations:
        _reject_backend_like_object(violation, "validation violation")
        v_data = _as_dict(violation)

        label = _val_rule_label(violation, v_data)
        severity = _val_severity(violation, v_data)
        status = _val_status(violation, v_data)
        message = _val_message(violation, v_data)
        cid = _as_str(
            _get_value(violation, "component_id",
            _get_value(violation, "cid",
            v_data.get("component_id",
            v_data.get("cid", "")))))

        # Build the value part of the row
        value_parts: list[str] = []
        if severity:
            value_parts.append(severity)
        if message:
            value_parts.append(message)
        if cid:
            value_parts.append(f"[{cid}]")
        value = " | ".join(value_parts) if value_parts else status

        row = (label, value)

        # Classify into sections — severity takes precedence for validation
        if severity == "ERROR" or status == "FAIL":
            error_rows.append(row)
            if message:
                all_warnings.append(f"{label}: {message}")
        elif severity == "WARNING" or status == "WARNING":
            warning_rows.append(row)
            if message:
                all_warnings.append(f"{label}: {message}")
        elif status == "PASS":
            passed_rows.append(row)
        elif severity == "INFO":
            info_rows.append(row)
        else:
            other_rows.append(row)

    # ── Build sections ─────────────────────────────────────────────
    sections: list[ReviewSectionReadModel] = []

    if error_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Errors",
                rows=tuple(error_rows),
                warnings=tuple(all_warnings),
            )
        )
    if warning_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Warnings",
                rows=tuple(warning_rows),
                warnings=tuple(all_warnings),
            )
        )
    if passed_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Passed",
                rows=tuple(passed_rows),
            )
        )
    if info_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Info",
                rows=tuple(info_rows),
            )
        )
    if other_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Other",
                rows=tuple(other_rows),
            )
        )

    return ReviewPanelReadModel(
        panel_name="Validation",
        sections=tuple(sections),
        available=True,
    )


def _cost_item_label(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe display label from a cost item object."""
    label = _as_str(
        _get_value(
            item, "item_label",
            _get_value(
                item, "label",
                _get_value(
                    item, "name",
                    data.get("item_label",
                             data.get("label",
                                      data.get("name", ""))),
                ),
            ),
        )
    )
    return label


def _cost_category(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe category string from a cost item."""
    cat = _as_str(
        _get_value(item, "item_category",
        _get_value(item, "category",
        data.get("item_category",
        data.get("category", "")))))
    return cat


def _cost_status(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe status string from a cost item."""
    status = _as_str(
        _get_value(item, "item_status",
        _get_value(item, "status",
        data.get("item_status",
        data.get("status", "")))))
    return status.upper() if status else ""


def _cost_severity(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe severity string from a cost item."""
    severity = _as_str(
        _get_value(item, "item_severity",
        _get_value(item, "severity",
        data.get("item_severity",
        data.get("severity", "")))))
    return severity.upper() if severity else ""


def _cost_amount(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe amount/value string from a cost item.

    Returns the amount as a string if present, else empty string.
    Does NOT calculate or infer amounts.
    """
    return _as_str(
        _get_value(item, "item_amount",
        _get_value(item, "amount",
        _get_value(item, "value",
        data.get("item_amount",
        data.get("amount",
        data.get("value", "")))))))


def _cost_currency(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe currency string from a cost item."""
    return _as_str(
        _get_value(item, "item_currency",
        _get_value(item, "currency",
        data.get("item_currency",
        data.get("currency", "")))))


def _cost_message(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe message/detail string from a cost item."""
    return _as_str(
        _get_value(item, "item_message",
        _get_value(item, "message",
        _get_value(item, "detail",
        data.get("item_message",
        data.get("message",
        data.get("detail", "")))))))


def build_cost_review_projection(
    source: Any = None,
) -> ReviewPanelReadModel:
    """Project duck-typed cost source into a ReviewPanelReadModel.

    Accepts:
    - An object with ``cost_items`` or ``line_items`` attribute
    - A dict with ``\"cost_items\"`` or ``\"line_items\"`` key
    - A list/tuple of cost item objects directly

    Each cost item may expose (via attribute or dict key):
    - ``item_label`` / ``label`` / ``name`` — display label
    - ``item_category`` / ``category`` — e.g. Material, Labor, Hardware, Total
    - ``item_status`` / ``status`` — e.g. ESTIMATED, CONFIRMED
    - ``item_severity`` / ``severity`` — e.g. INFO, WARNING
    - ``item_amount`` / ``amount`` / ``value`` — numeric amount as string
    - ``item_currency`` / ``currency`` — e.g. USD, EUR
    - ``item_message`` / ``message`` / ``detail`` — detail text
    - ``component_id`` — optional linked component ID

    Items are grouped into sections by category: Totals, Material, Labor,
    Hardware, Waste, Margin, Other.

    Does NOT calculate cost, margin, profit, or waste. Only projects
    already-existing values.

    Returns a ReviewPanelReadModel with panel_name=\"Cost\".
    No raw cost objects leak into the output.
    """
    _reject_backend_like_object(source, "cost source")

    if source is None:
        return ReviewPanelReadModel(
            panel_name="Cost",
            available=False,
        )

    # ── Extract raw cost items ─────────────────────────────────────
    data = _as_dict(source)
    raw_items = _get_value(source, "cost_items",
                 _get_value(source, "line_items",
                 data.get("cost_items",
                 data.get("line_items", None))))

    if raw_items is None:
        if isinstance(source, (list, tuple)):
            raw_items = source
        elif hasattr(source, "__iter__") and not isinstance(source, (str, bytes, Mapping)):
            raw_items = list(source)
        else:
            raw_items = ()

    if not raw_items:
        return ReviewPanelReadModel(
            panel_name="Cost",
            sections=(
                ReviewSectionReadModel(
                    section_name="Cost Breakdown",
                    rows=(("Status", "No cost data"),),
                    warnings=("Cost data not available",),
                ),
            ),
            available=False,
        )

    # ── Convert each cost item to a row ────────────────────────────
    totals_rows: list[tuple[str, str]] = []
    material_rows: list[tuple[str, str]] = []
    labor_rows: list[tuple[str, str]] = []
    hardware_rows: list[tuple[str, str]] = []
    waste_rows: list[tuple[str, str]] = []
    margin_rows: list[tuple[str, str]] = []
    other_rows: list[tuple[str, str]] = []
    all_warnings: list[str] = []

    for item in raw_items:
        _reject_backend_like_object(item, "cost item")
        item_data = _as_dict(item)

        label = _cost_item_label(item, item_data)
        category = _cost_category(item, item_data)
        status = _cost_status(item, item_data)
        severity = _cost_severity(item, item_data)
        amount = _cost_amount(item, item_data)
        currency = _cost_currency(item, item_data)
        message = _cost_message(item, item_data)
        cid = _as_str(
            _get_value(item, "component_id",
            _get_value(item, "cid",
            item_data.get("component_id",
            item_data.get("cid", "")))))

        # Build the value part of the row
        value_parts: list[str] = []
        if amount:
            value_parts.append(amount)
        if currency:
            value_parts.append(currency)
        if status:
            value_parts.append(status)
        if severity:
            value_parts.append(severity)
        if message:
            value_parts.append(message)
        if cid:
            value_parts.append(f"[{cid}]")
        value = " | ".join(value_parts) if value_parts else label

        row = (label, value)

        # Group by category — case-insensitive
        cat_lower = category.lower()
        if cat_lower in ("total", "totals"):
            totals_rows.append(row)
        elif cat_lower == "material":
            material_rows.append(row)
        elif cat_lower == "labor":
            labor_rows.append(row)
        elif cat_lower == "hardware":
            hardware_rows.append(row)
        elif cat_lower == "waste":
            waste_rows.append(row)
        elif cat_lower == "margin":
            margin_rows.append(row)
        else:
            other_rows.append(row)

        if severity and severity in ("WARNING", "ERROR", "BLOCKER"):
            all_warnings.append(f"{label}: {message or severity}")
        if status and status in ("FAIL", "WARNING"):
            all_warnings.append(f"{label}: {message or status}")

    # ── Build sections ─────────────────────────────────────────────
    sections: list[ReviewSectionReadModel] = []

    # Totals first (if present) — highest business value
    if totals_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Totals",
                rows=tuple(totals_rows),
            )
        )

    if material_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Material",
                rows=tuple(material_rows),
            )
        )
    if labor_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Labor",
                rows=tuple(labor_rows),
            )
        )
    if hardware_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Hardware",
                rows=tuple(hardware_rows),
            )
        )
    if waste_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Waste",
                rows=tuple(waste_rows),
            )
        )
    if margin_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Margin",
                rows=tuple(margin_rows),
            )
        )
    if other_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Other",
                rows=tuple(other_rows),
            )
        )

    return ReviewPanelReadModel(
        panel_name="Cost",
        sections=tuple(sections),
        available=True,
    )


def _com_label(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe display label from a commercial item."""
    label = _as_str(
        _get_value(
            item, "item_label",
            _get_value(
                item, "label",
                _get_value(
                    item, "name",
                    data.get("item_label",
                             data.get("label",
                                      data.get("name", ""))),
                ),
            ),
        )
    )
    return label


def _com_status(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe status string from a commercial item."""
    status = _as_str(
        _get_value(item, "item_status",
        _get_value(item, "status",
        data.get("item_status",
        data.get("status", "")))))
    return status.upper() if status else ""


def _com_severity(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe severity string from a commercial item."""
    severity = _as_str(
        _get_value(item, "item_severity",
        _get_value(item, "severity",
        data.get("item_severity",
        data.get("severity", "")))))
    return severity.upper() if severity else ""


def _com_category(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe category string from a commercial item."""
    return _as_str(
        _get_value(item, "item_category",
        _get_value(item, "category",
        data.get("item_category",
        data.get("category", "")))))


def _com_value(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe value/amount string from a commercial item.

    Projects already-computed values only — never calculates.
    """
    return _as_str(
        _get_value(item, "item_value",
        _get_value(item, "value",
        _get_value(item, "amount",
        data.get("item_value",
        data.get("value",
        data.get("amount", "")))))))


def _com_currency(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe currency string from a commercial item."""
    return _as_str(
        _get_value(item, "item_currency",
        _get_value(item, "currency",
        data.get("item_currency",
        data.get("currency", "")))))


def _com_message(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe message/summary/detail string from a commercial item."""
    return _as_str(
        _get_value(item, "item_message",
        _get_value(item, "message",
        _get_value(item, "summary",
        _get_value(item, "detail",
        data.get("item_message",
        data.get("message",
        data.get("summary",
        data.get("detail", "")))))))))


def _com_note(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe customer-visible note from a commercial item."""
    return _as_str(
        _get_value(item, "customer_note",
        _get_value(item, "note",
        data.get("customer_note",
        data.get("note", "")))))


def build_commercial_review_projection(
    source: Any = None,
) -> ReviewPanelReadModel:
    """Project duck-typed commercial source into a ReviewPanelReadModel.

    Accepts:
    - An object with ``commercial_items`` or ``line_items`` attribute
    - A dict with ``\"commercial_items\"`` or ``\"line_items\"`` key
    - A list/tuple of commercial item objects directly

    Each commercial item may expose (via attribute or dict key):
    - ``item_label`` / ``label`` / ``name`` — display label
    - ``item_status`` / ``status`` — e.g. DRAFT, CONFIRMED, SENT
    - ``item_severity`` / ``severity`` — e.g. INFO, WARNING
    - ``item_category`` / ``category`` — e.g. Pricing, Discounts, Terms, Summary
    - ``item_value`` / ``value`` / ``amount`` — already-computed value
    - ``item_currency`` / ``currency`` — e.g. USD, EUR
    - ``item_message`` / ``message`` / ``summary`` / ``detail`` — detail text
    - ``customer_note`` / ``note`` — customer-visible note
    - ``component_id`` — optional linked component ID

    Items are grouped into sections by category: Pricing, Discounts, Terms,
    Summary, Notes, Other.

    Does NOT calculate quotation, discount, profit, margin, markup, tax,
    or pricing recommendations. Only projects already-existing values.

    Returns a ReviewPanelReadModel with panel_name=\"Commercial\".
    No raw commercial objects leak into the output.
    """
    _reject_backend_like_object(source, "commercial source")

    if source is None:
        return ReviewPanelReadModel(
            panel_name="Commercial",
            available=False,
        )

    # ── Extract raw commercial items ───────────────────────────────
    data = _as_dict(source)
    raw_items = _get_value(source, "commercial_items",
                 _get_value(source, "line_items",
                 data.get("commercial_items",
                 data.get("line_items", None))))

    if raw_items is None:
        if isinstance(source, (list, tuple)):
            raw_items = source
        elif hasattr(source, "__iter__") and not isinstance(source, (str, bytes, Mapping)):
            raw_items = list(source)
        else:
            raw_items = ()

    if not raw_items:
        return ReviewPanelReadModel(
            panel_name="Commercial",
            sections=(
                ReviewSectionReadModel(
                    section_name="Commercial Items",
                    rows=(("Status", "No commercial data"),),
                    warnings=("Commercial data not available",),
                ),
            ),
            available=False,
        )

    # ── Convert each item to a row ─────────────────────────────────
    pricing_rows: list[tuple[str, str]] = []
    discount_rows: list[tuple[str, str]] = []
    terms_rows: list[tuple[str, str]] = []
    summary_rows: list[tuple[str, str]] = []
    notes_rows: list[tuple[str, str]] = []
    other_rows: list[tuple[str, str]] = []
    all_warnings: list[str] = []

    for item in raw_items:
        _reject_backend_like_object(item, "commercial item")
        item_data = _as_dict(item)

        label = _com_label(item, item_data)
        category = _com_category(item, item_data)
        status = _com_status(item, item_data)
        severity = _com_severity(item, item_data)
        value = _com_value(item, item_data)
        currency = _com_currency(item, item_data)
        message = _com_message(item, item_data)
        note = _com_note(item, item_data)
        cid = _as_str(
            _get_value(item, "component_id",
            _get_value(item, "cid",
            item_data.get("component_id",
            item_data.get("cid", "")))))

        # Build the value part of the row
        value_parts: list[str] = []
        if value:
            value_parts.append(value)
        if currency:
            value_parts.append(currency)
        if status:
            value_parts.append(status)
        if severity:
            value_parts.append(severity)
        if message:
            value_parts.append(message)
        if note:
            value_parts.append(f"[note: {note}]")
        if cid:
            value_parts.append(f"[{cid}]")
        row_value = " | ".join(value_parts) if value_parts else label

        row = (label, row_value)

        # Group by category — case-insensitive
        cat_lower = category.lower()
        if cat_lower in ("pricing", "price"):
            pricing_rows.append(row)
        elif cat_lower in ("discount", "discounts"):
            discount_rows.append(row)
        elif cat_lower in ("terms", "term"):
            terms_rows.append(row)
        elif cat_lower in ("summary", "total", "totals"):
            summary_rows.append(row)
        elif cat_lower in ("note", "notes", "customer_note"):
            notes_rows.append(row)
        else:
            other_rows.append(row)

        if severity and severity in ("WARNING", "ERROR", "BLOCKER"):
            all_warnings.append(f"{label}: {message or severity}")
        if status and status in ("FAIL", "WARNING"):
            all_warnings.append(f"{label}: {message or status}")

    # ── Build sections ─────────────────────────────────────────────
    sections: list[ReviewSectionReadModel] = []

    if pricing_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Pricing",
                rows=tuple(pricing_rows),
            )
        )
    if discount_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Discounts",
                rows=tuple(discount_rows),
            )
        )
    if terms_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Terms",
                rows=tuple(terms_rows),
            )
        )
    if summary_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Summary",
                rows=tuple(summary_rows),
            )
        )
    if notes_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Notes",
                rows=tuple(notes_rows),
            )
        )
    if other_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Other",
                rows=tuple(other_rows),
            )
        )
    if all_warnings and not any(s.warnings for s in sections):
        sections.append(
            ReviewSectionReadModel(
                section_name="Warnings",
                warnings=tuple(sorted(set(all_warnings))),
            )
        )

    return ReviewPanelReadModel(
        panel_name="Commercial",
        sections=tuple(sections),
        available=True,
    )


def _rel_label(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe display label from a release item."""
    label = _as_str(
        _get_value(
            item, "item_label",
            _get_value(
                item, "label",
                _get_value(
                    item, "name",
                    data.get("item_label",
                             data.get("label",
                                      data.get("name", ""))),
                ),
            ),
        )
    )
    return label


def _rel_status(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe status string from a release item."""
    status = _as_str(
        _get_value(item, "item_status",
        _get_value(item, "status",
        data.get("item_status",
        data.get("status", "")))))
    return status.upper() if status else ""


def _rel_severity(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe severity string from a release item."""
    severity = _as_str(
        _get_value(item, "item_severity",
        _get_value(item, "severity",
        data.get("item_severity",
        data.get("severity", "")))))
    return severity.upper() if severity else ""


def _rel_category(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe category string from a release item."""
    return _as_str(
        _get_value(item, "item_category",
        _get_value(item, "category",
        data.get("item_category",
        data.get("category", "")))))


def _rel_message(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe message/detail string from a release item."""
    return _as_str(
        _get_value(item, "item_message",
        _get_value(item, "message",
        _get_value(item, "detail",
        data.get("item_message",
        data.get("message",
        data.get("detail", "")))))))


def _rel_timestamp(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe timestamp/date string from a release item.

    Projects already-existing timestamps only — never infers or computes dates.
    """
    return _as_str(
        _get_value(item, "item_timestamp",
        _get_value(item, "timestamp",
        _get_value(item, "date",
        data.get("item_timestamp",
        data.get("timestamp",
        data.get("date", "")))))))


def _rel_reviewer(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe reviewer/approver label from a release item."""
    return _as_str(
        _get_value(item, "reviewer",
        _get_value(item, "approver",
        data.get("reviewer",
        data.get("approver", "")))))


def _rel_note(item: Any, data: dict[str, Any]) -> str:
    """Extract a safe note string from a release item."""
    return _as_str(
        _get_value(item, "customer_note",
        _get_value(item, "note",
        data.get("customer_note",
        data.get("note", "")))))


def build_release_review_projection(
    source: Any = None,
) -> ReviewPanelReadModel:
    """Project duck-typed release source into a ReviewPanelReadModel.

    Accepts:
    - An object with ``release_items``, ``checklist_items``, or ``approvals``
    - A dict with ``\"release_items\"``, ``\"checklist_items\"``, or ``\"approvals\"``
    - A list/tuple of release item objects directly

    Each release item may expose (via attribute or dict key):
    - ``item_label`` / ``label`` / ``name`` — display label
    - ``item_status`` / ``status`` — e.g. RELEASED, PENDING, BLOCKED
    - ``item_severity`` / ``severity`` — e.g. INFO, WARNING, BLOCKER
    - ``item_category`` / ``category`` — e.g. Checklist, Approval, Blocked, Note
    - ``item_message`` / ``message`` / ``detail`` — detail text
    - ``item_timestamp`` / ``timestamp`` / ``date`` — already-computed date
    - ``reviewer`` / ``approver`` — approver label
    - ``customer_note`` / ``note`` — attached note
    - ``component_id`` — optional linked component ID

    Items are grouped into sections by category: Checklist, Approvals, Ready,
    Blocked, Notes, Warnings, Other.

    Does NOT calculate release readiness, approval status, blocking status,
    or infer any release decision. Only projects already-existing values.

    Returns a ReviewPanelReadModel with panel_name=\"Release\".
    No raw release objects leak into the output.
    """
    _reject_backend_like_object(source, "release source")

    if source is None:
        return ReviewPanelReadModel(
            panel_name="Release",
            available=False,
        )

    # ── Extract raw release items ──────────────────────────────────
    data = _as_dict(source)
    raw_items = _get_value(source, "release_items",
                 _get_value(source, "checklist_items",
                 _get_value(source, "approvals",
                 data.get("release_items",
                 data.get("checklist_items",
                 data.get("approvals", None))))))

    if raw_items is None:
        if isinstance(source, (list, tuple)):
            raw_items = source
        elif hasattr(source, "__iter__") and not isinstance(source, (str, bytes, Mapping)):
            raw_items = list(source)
        else:
            raw_items = ()

    if not raw_items:
        return ReviewPanelReadModel(
            panel_name="Release",
            sections=(
                ReviewSectionReadModel(
                    section_name="Release Checklist",
                    rows=(("Status", "No release data"),),
                    warnings=("Release data not available",),
                ),
            ),
            available=False,
        )

    # ── Convert each item to a row ─────────────────────────────────
    checklist_rows: list[tuple[str, str]] = []
    approval_rows: list[tuple[str, str]] = []
    ready_rows: list[tuple[str, str]] = []
    blocked_rows: list[tuple[str, str]] = []
    notes_rows: list[tuple[str, str]] = []
    other_rows: list[tuple[str, str]] = []
    all_warnings: list[str] = []

    for item in raw_items:
        _reject_backend_like_object(item, "release item")
        item_data = _as_dict(item)

        label = _rel_label(item, item_data)
        category = _rel_category(item, item_data)
        status = _rel_status(item, item_data)
        severity = _rel_severity(item, item_data)
        message = _rel_message(item, item_data)
        timestamp = _rel_timestamp(item, item_data)
        reviewer = _rel_reviewer(item, item_data)
        note = _rel_note(item, item_data)
        cid = _as_str(
            _get_value(item, "component_id",
            _get_value(item, "cid",
            item_data.get("component_id",
            item_data.get("cid", "")))))

        # Build the value part of the row
        value_parts: list[str] = []
        if status:
            value_parts.append(status)
        if severity:
            value_parts.append(severity)
        if message:
            value_parts.append(message)
        if timestamp:
            value_parts.append(timestamp)
        if reviewer:
            value_parts.append(f"[by: {reviewer}]")
        if note:
            value_parts.append(f"[note: {note}]")
        if cid:
            value_parts.append(f"[{cid}]")
        row_value = " | ".join(value_parts) if value_parts else label

        row = (label, row_value)

        # Group by category — case-insensitive
        cat_lower = category.lower()
        if cat_lower in ("checklist", "checklist item", "checklist_item"):
            checklist_rows.append(row)
        elif cat_lower in ("approval", "approvals", "signoff", "sign-off"):
            approval_rows.append(row)
        elif cat_lower in ("ready", "released", "done", "complete"):
            ready_rows.append(row)
        elif cat_lower in ("blocked", "blocker", "fail"):
            blocked_rows.append(row)
        elif cat_lower in ("note", "notes", "customer_note"):
            notes_rows.append(row)
        else:
            other_rows.append(row)

        if severity and severity in ("WARNING", "ERROR", "BLOCKER"):
            all_warnings.append(f"{label}: {message or severity}")
        if status and status in ("BLOCKED", "FAIL", "WARNING"):
            all_warnings.append(f"{label}: {message or status}")

    # ── Build sections ─────────────────────────────────────────────
    sections: list[ReviewSectionReadModel] = []

    if blocked_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Blocked",
                rows=tuple(blocked_rows),
                warnings=tuple(all_warnings),
            )
        )
    if checklist_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Checklist",
                rows=tuple(checklist_rows),
            )
        )
    if approval_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Approvals",
                rows=tuple(approval_rows),
            )
        )
    if ready_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Ready",
                rows=tuple(ready_rows),
            )
        )
    if notes_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Notes",
                rows=tuple(notes_rows),
            )
        )
    if other_rows:
        sections.append(
            ReviewSectionReadModel(
                section_name="Other",
                rows=tuple(other_rows),
            )
        )
    if all_warnings and not any(s.warnings for s in sections):
        sections.append(
            ReviewSectionReadModel(
                section_name="Warnings",
                warnings=tuple(sorted(set(all_warnings))),
            )
        )

    return ReviewPanelReadModel(
        panel_name="Release",
        sections=tuple(sections),
        available=True,
    )


def build_manufacturing_render_review_section(
    commands: Any = None,
) -> ReviewSectionReadModel:
    """Extract manufacturing rendering metadata from viewport commands.

    Accepts an iterable of viewport command dicts (SceneRenderer output)
    or a single command dict.  Scans for the rendering-only metadata
    fields that SceneRenderer derives from overlay data:

      review_priority, review_category, hole_style,
      drill_direction, hole_depth, hole_depth_mode

    Returns a ReviewSectionReadModel with one row per distinct metadata
    field found.  When no commands or no known fields are present,
    returns an empty section with no rows (section_name is always
    ``\"Rendering Details\"``).

    This is a pure side-effect-free consumption of renderer output.
    No manufacturing logic, no cost logic, no re-computation of values.
    """
    section_name = "Rendering Details"
    if commands is None:
        return ReviewSectionReadModel(section_name=section_name)

    if isinstance(commands, Mapping) and not isinstance(commands, (list, tuple)):
        commands = [commands]

    known_fields = frozenset({
        "review_priority",
        "review_category",
        "hole_style",
        "drill_direction",
        "hole_depth",
        "hole_depth_mode",
        "review_mode",
    })
    collected: dict[str, set[str]] = {
        k: set()
        for k in known_fields
    }

    for cmd in commands or ():
        if not isinstance(cmd, Mapping):
            continue
        for field in known_fields:
            raw = cmd.get(field)
            if raw is not None:
                collected[field].add(_as_str(raw))

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

    if not rows and not any(collected[field] for field in known_fields):
        return ReviewSectionReadModel(section_name=section_name)

    return ReviewSectionReadModel(
        section_name=section_name,
        rows=tuple(rows),
    )


# ── Specification-to-Inspector enrichment ──────────────────────────


def _specification_dimension_fields(specification: Any) -> tuple[dict[str, Any], ...]:
    """Build inspector field dicts from an engineering specification.

    Returns field dicts for width_mm, height_mm, depth_mm (dimensions
    with unit "mm"), shelf_count (integer count), and door_count
    (integer count).  Each field uses ``getattr`` with a safe default
    so any specification-like object is accepted without domain imports.

    Non-destructive — never mutates the specification.
    """
    if specification is None:
        return ()
    return (
        {
            "name": "width_mm",
            "label": "Width",
            "value": str(getattr(specification, "width_mm", "")),
            "unit": "mm",
            "editable": True,
            "source_reference": "ActiveEngineeringState.specification",
            "group": "Geometry",
        },
        {
            "name": "height_mm",
            "label": "Height",
            "value": str(getattr(specification, "height_mm", "")),
            "unit": "mm",
            "editable": True,
            "source_reference": "ActiveEngineeringState.specification",
            "group": "Geometry",
        },
        {
            "name": "depth_mm",
            "label": "Depth",
            "value": str(getattr(specification, "depth_mm", "")),
            "unit": "mm",
            "editable": True,
            "source_reference": "ActiveEngineeringState.specification",
            "group": "Geometry",
        },
        {
            "name": "shelf_count",
            "label": "Shelf Count",
            "value": str(getattr(specification, "shelf_count", "")),
            "unit": "",
            "editable": True,
            "source_reference": "ActiveEngineeringState.specification",
            "group": "Configuration",
        },
        {
            "name": "door_count",
            "label": "Door Count",
            "value": str(getattr(specification, "door_count", "")),
            "unit": "",
            "editable": True,
            "source_reference": "ActiveEngineeringState.specification",
            "group": "Configuration",
        },
    )


def enrich_inspector_source_with_specification(
    source: Any,
    engineering_state: Any,
) -> dict[str, Any]:
    """Enrich an inspector source dict with specification dimension fields.

    Returns a new dict based on *source* (converted to a flat dict via
    ``_as_dict``) with ``width_mm``, ``height_mm``, ``depth_mm`` field
    entries prepended to the ``fields`` list under the ``Geometry`` group.

    Existing fields from the original source are preserved.
    When *engineering_state* is None or carries no specification, the
    source is returned as a plain dict with no enrichment.

    Never mutates *source*, *engineering_state*, or the specification.
    """
    if engineering_state is None:
        return _as_dict(source) if not isinstance(source, Mapping) else dict(source)

    specification = getattr(engineering_state, "specification", None)
    if specification is None:
        return _as_dict(source) if not isinstance(source, Mapping) else dict(source)

    enriched = _as_dict(source) if not isinstance(source, Mapping) else dict(source)

    spec_fields = _specification_dimension_fields(specification)
    existing_fields = enriched.get("fields", ())
    if isinstance(existing_fields, (tuple, list)) and existing_fields:
        enriched["fields"] = list(spec_fields) + list(existing_fields)
    else:
        enriched["fields"] = list(spec_fields)

    return enriched


__all__ = [
    "build_project_tree_read_model",
    "build_inspector_read_model",
    "build_preview_read_model",
    "build_message_center_read_model",
    "build_review_panel_read_models",
    "build_manufacturing_review_projection",
    "build_manufacturing_render_review_section",
    "build_validation_review_projection",
    "build_cost_review_projection",
    "build_commercial_review_projection",
    "build_release_review_projection",
    "enrich_inspector_source_with_specification",
]
