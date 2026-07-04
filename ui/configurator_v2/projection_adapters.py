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
    )


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
    items_source = _get_value(source, "items", data.get("items", ()))
    return PreviewReadModel(
        preview_mode=_as_str(preview_mode if preview_mode is not None else data.get("preview_mode", "Customer View")),
        items=tuple(_build_preview_item(item) for item in (items_source or ())),
        highlighted_item_id=_as_str(highlighted_item_id if highlighted_item_id is not None else data.get("highlighted_item_id", "")),
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


__all__ = [
    "build_project_tree_read_model",
    "build_inspector_read_model",
    "build_preview_read_model",
    "build_message_center_read_model",
    "build_review_panel_read_models",
]
