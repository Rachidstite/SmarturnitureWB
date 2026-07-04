from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Iterable, Mapping
from typing import Any


def _ensure_str(value, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    return value


def _ensure_bool(value, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be a bool")
    return value


def _ensure_float(value, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be numeric")
    return float(value)


def _ensure_triplet(value, field_name: str) -> tuple[float, float, float]:
    if value is None:
        return (0.0, 0.0, 0.0)
    if isinstance(value, (str, bytes)):
        raise TypeError(f"{field_name} must be a 3-item numeric sequence")
    items = tuple(value)
    if len(items) != 3:
        raise TypeError(f"{field_name} must contain exactly 3 items")
    return tuple(_ensure_float(item, f"{field_name}[{index}]") for index, item in enumerate(items))


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


def _as_dict(source: Any) -> dict[str, Any]:
    if source is None:
        return {}
    if isinstance(source, Mapping):
        return dict(source)
    if hasattr(source, "__dict__"):
        return {key: value for key, value in vars(source).items() if not key.startswith("_")}
    return {}


def _get_value(source: Any, key: str, default: Any = None) -> Any:
    if source is None:
        return default
    if isinstance(source, Mapping):
        return source.get(key, default)
    return getattr(source, key, default)


def _reject_backend_like_object(value: Any, field_name: str):
    if value is None:
        return
    value_type = type(value)
    module_name = getattr(value_type, "__module__", "")
    if module_name.startswith(("FreeCAD", "Part", "Sketcher")):
        raise TypeError(f"{field_name} cannot contain backend geometry objects")
    if any(hasattr(value, attr) for attr in ("Shape", "ViewObject", "Document")):
        raise TypeError(f"{field_name} cannot contain backend geometry objects")


@dataclass(frozen=True)
class SceneBoundsProjection:
    minimum: tuple[float, float, float] = (0.0, 0.0, 0.0)
    maximum: tuple[float, float, float] = (0.0, 0.0, 0.0)
    source_reference: str = ""

    def __post_init__(self):
        object.__setattr__(self, "minimum", _ensure_triplet(self.minimum, "minimum"))
        object.__setattr__(self, "maximum", _ensure_triplet(self.maximum, "maximum"))
        object.__setattr__(self, "source_reference", _ensure_str(self.source_reference, "source_reference"))

    @property
    def display_label(self) -> str:
        return f"min={self.minimum} max={self.maximum}"


@dataclass(frozen=True)
class SceneNodeProjection:
    node_id: str = ""
    parent_id: str = ""
    node_type: str = ""
    display_name: str = ""
    visible: bool = True
    selectable: bool = True
    bounding_box: SceneBoundsProjection = field(default_factory=SceneBoundsProjection)
    transform: tuple[float, float, float] = (0.0, 0.0, 0.0)
    display_metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    source_reference: str = ""

    def __post_init__(self):
        object.__setattr__(self, "node_id", _ensure_str(self.node_id, "node_id"))
        object.__setattr__(self, "parent_id", _ensure_str(self.parent_id, "parent_id"))
        object.__setattr__(self, "node_type", _ensure_str(self.node_type, "node_type"))
        object.__setattr__(self, "display_name", _ensure_str(self.display_name, "display_name"))
        object.__setattr__(self, "visible", _ensure_bool(self.visible, "visible"))
        object.__setattr__(self, "selectable", _ensure_bool(self.selectable, "selectable"))
        object.__setattr__(self, "bounding_box", _ensure_scene_bounds_projection(self.bounding_box, "bounding_box"))
        object.__setattr__(self, "transform", _ensure_triplet(self.transform, "transform"))
        object.__setattr__(self, "display_metadata", _ensure_string_pairs(self.display_metadata, "display_metadata"))
        object.__setattr__(self, "source_reference", _ensure_str(self.source_reference, "source_reference"))


@dataclass(frozen=True)
class SceneSelectionProjection:
    selected_node_id: str = ""
    display_name: str = ""
    node_type: str = ""
    highlight_target: str = ""
    source_reference: str = ""
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        object.__setattr__(self, "selected_node_id", _ensure_str(self.selected_node_id, "selected_node_id"))
        object.__setattr__(self, "display_name", _ensure_str(self.display_name, "display_name"))
        object.__setattr__(self, "node_type", _ensure_str(self.node_type, "node_type"))
        object.__setattr__(self, "highlight_target", _ensure_str(self.highlight_target, "highlight_target"))
        object.__setattr__(self, "source_reference", _ensure_str(self.source_reference, "source_reference"))
        object.__setattr__(self, "warnings", tuple(_ensure_str(warning, "warnings") for warning in (self.warnings or ())))


@dataclass(frozen=True)
class SceneProjection:
    scene_available: bool = False
    nodes: tuple[SceneNodeProjection, ...] = field(default_factory=tuple)
    bounds: SceneBoundsProjection = field(default_factory=SceneBoundsProjection)
    selection: SceneSelectionProjection = field(default_factory=SceneSelectionProjection)
    highlight_target: str = ""
    representation_status: str = "Unavailable"
    warnings: tuple[str, ...] = field(default_factory=tuple)
    source_reference: str = ""
    node_count: int = 0

    def __post_init__(self):
        object.__setattr__(self, "scene_available", _ensure_bool(self.scene_available, "scene_available"))
        object.__setattr__(self, "nodes", _ensure_node_tuple(self.nodes, "nodes"))
        object.__setattr__(self, "bounds", _ensure_scene_bounds_projection(self.bounds, "bounds"))
        object.__setattr__(self, "selection", _ensure_scene_selection_projection(self.selection, "selection"))
        object.__setattr__(self, "highlight_target", _ensure_str(self.highlight_target, "highlight_target"))
        object.__setattr__(self, "representation_status", _ensure_str(self.representation_status, "representation_status"))
        object.__setattr__(self, "warnings", tuple(_ensure_str(warning, "warnings") for warning in (self.warnings or ())))
        object.__setattr__(self, "source_reference", _ensure_str(self.source_reference, "source_reference"))
        object.__setattr__(self, "node_count", _ensure_node_count(self.node_count, "node_count"))


def _ensure_scene_bounds_projection(value, field_name: str) -> SceneBoundsProjection:
    if isinstance(value, SceneBoundsProjection):
        return value
    if value is None:
        return SceneBoundsProjection()
    if isinstance(value, Mapping):
        return SceneBoundsProjection(
            minimum=value.get("minimum", value.get("min", (0.0, 0.0, 0.0))),
            maximum=value.get("maximum", value.get("max", (0.0, 0.0, 0.0))),
            source_reference=value.get("source_reference", ""),
        )
    raise TypeError(f"{field_name} must be a SceneBoundsProjection")


def _ensure_scene_selection_projection(value, field_name: str) -> SceneSelectionProjection:
    if isinstance(value, SceneSelectionProjection):
        return value
    if value is None:
        return SceneSelectionProjection()
    if isinstance(value, Mapping):
        return SceneSelectionProjection(
            selected_node_id=value.get("selected_node_id", value.get("node_id", "")),
            display_name=value.get("display_name", value.get("label", "")),
            node_type=value.get("node_type", value.get("selection_type", "")),
            highlight_target=value.get("highlight_target", value.get("selected_node_id", "")),
            source_reference=value.get("source_reference", ""),
            warnings=value.get("warnings", ()),
        )
    raise TypeError(f"{field_name} must be a SceneSelectionProjection")


def _ensure_node_tuple(value, field_name: str) -> tuple[SceneNodeProjection, ...]:
    if value is None:
        return ()
    items = []
    for item in value:
        if not isinstance(item, SceneNodeProjection):
            raise TypeError(f"{field_name} must contain SceneNodeProjection instances")
        items.append(item)
    return tuple(items)


def _ensure_node_count(value, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value < 0:
        raise TypeError(f"{field_name} must be non-negative")
    return value


def _safe_display_name(node: Any, node_id: str, node_type: str) -> str:
    data = _as_dict(node)
    label = _get_value(node, "display_name", _get_value(node, "label", data.get("display_name", data.get("label", ""))))
    if not label:
        label = _get_value(node, "name", data.get("name", ""))
    if not label:
        label = node_type or node_id
    return _ensure_str(str(label), "display_name")


def _safe_node_type(node: Any) -> str:
    data = _as_dict(node)
    node_type = _get_value(node, "node_type", _get_value(node, "type", data.get("node_type", data.get("type", ""))))
    if not node_type:
        role = _get_value(node, "role", data.get("role", ""))
        node_type = getattr(role, "name", role)
    return _ensure_str(str(node_type or ""), "node_type")


def _safe_node_id(node: Any, default: str = "") -> str:
    data = _as_dict(node)
    node_id = _get_value(node, "node_id", _get_value(node, "id", data.get("node_id", data.get("id", default))))
    identity = _get_value(node, "identity", data.get("identity", None))
    if not node_id and identity is not None:
        node_id = getattr(identity, "key", "")
    return _ensure_str(str(node_id or default or ""), "node_id")


def _safe_parent_id(node: Any) -> str:
    data = _as_dict(node)
    parent_id = _get_value(node, "parent_id", data.get("parent_id", ""))
    if not parent_id:
        parent_id = _get_value(node, "parent", data.get("parent", ""))
    return _ensure_str(str(parent_id or ""), "parent_id")


def _safe_visible(node: Any) -> bool:
    data = _as_dict(node)
    value = _get_value(node, "visible", data.get("visible", True))
    return bool(True if value is None else value)


def _safe_selectable(node: Any) -> bool:
    data = _as_dict(node)
    value = _get_value(node, "selectable", data.get("selectable", True))
    return bool(True if value is None else value)


def _safe_transform(node: Any) -> tuple[float, float, float]:
    data = _as_dict(node)
    transform = _get_value(node, "transform", data.get("transform", None))
    if transform is not None:
        if hasattr(transform, "x") and hasattr(transform, "y") and hasattr(transform, "z"):
            return (_ensure_float(transform.x, "transform.x"), _ensure_float(transform.y, "transform.y"), _ensure_float(transform.z, "transform.z"))
        return _ensure_triplet(transform, "transform")
    x = _ensure_float(_get_value(node, "x", data.get("x", 0.0)), "x")
    y = _ensure_float(_get_value(node, "y", data.get("y", 0.0)), "y")
    z = _ensure_float(_get_value(node, "z", data.get("z", 0.0)), "z")
    return (x, y, z)


def _safe_bounding_box(node: Any) -> SceneBoundsProjection:
    data = _as_dict(node)
    width = _ensure_float(_get_value(node, "width", data.get("width", 0.0)), "width")
    depth = _ensure_float(_get_value(node, "depth", data.get("depth", 0.0)), "depth")
    height = _ensure_float(_get_value(node, "height", data.get("height", 0.0)), "height")
    x, y, z = _safe_transform(node)
    return SceneBoundsProjection(
        minimum=(x, y, z),
        maximum=(x + max(width, 0.0), y + max(depth, 0.0), z + max(height, 0.0)),
        source_reference=_safe_source_reference(node),
    )


def _safe_metadata(node: Any) -> tuple[tuple[str, str], ...]:
    data = _as_dict(node)
    metadata = _get_value(node, "display_metadata", data.get("display_metadata", None))
    if metadata is None:
        metadata = _get_value(node, "metadata", data.get("metadata", {}))
    if isinstance(metadata, Mapping):
        items = metadata.items()
    else:
        items = metadata or ()
    pairs = []
    for key, value in items:
        if key in {"Shape", "ViewObject", "Document"}:
            continue
        pairs.append((_ensure_str(str(key), "display_metadata.key"), _ensure_str(str(value), "display_metadata.value")))
    return tuple(pairs)


def _safe_source_reference(node: Any) -> str:
    data = _as_dict(node)
    source_reference = _get_value(node, "source_reference", data.get("source_reference", ""))
    if not source_reference:
        identity = _get_value(node, "identity", data.get("identity", None))
        source_reference = getattr(identity, "key", "")
    return _ensure_str(str(source_reference or ""), "source_reference")


def _scene_node_from_source(node: Any, parent_id: str = "") -> SceneNodeProjection:
    _reject_backend_like_object(node, "scene node")
    node_id = _safe_node_id(node)
    node_type = _safe_node_type(node)
    display_name = _safe_display_name(node, node_id, node_type)
    data = _as_dict(node)
    node_parent_id = _safe_parent_id(node) or parent_id
    children = _get_value(node, "children", data.get("children", ()))
    # Children are flattened by the builder; only the safe current node is projected here.
    _ = children
    return SceneNodeProjection(
        node_id=node_id,
        parent_id=node_parent_id,
        node_type=node_type,
        display_name=display_name,
        visible=_safe_visible(node),
        selectable=_safe_selectable(node),
        bounding_box=_safe_bounding_box(node),
        transform=_safe_transform(node),
        display_metadata=_safe_metadata(node),
        source_reference=_safe_source_reference(node),
    )


def _iter_scene_nodes(source: Any) -> Iterable[Any]:
    if source is None:
        return ()
    if isinstance(source, Mapping):
        if "all_nodes" in source and callable(source["all_nodes"]):
            return tuple(source["all_nodes"]() or ())
        if "nodes" in source:
            return tuple(source.get("nodes", ()) or ())
        if "scene_graph" in source:
            return _iter_scene_nodes(source["scene_graph"])
    if hasattr(source, "all_nodes") and callable(getattr(source, "all_nodes")):
        return tuple(source.all_nodes() or ())
    if hasattr(source, "nodes"):
        return tuple(getattr(source, "nodes", ()) or ())
    return ()


def _flatten_scene_nodes(source: Any, *, parent_id: str = "") -> tuple[SceneNodeProjection, ...]:
    result: list[SceneNodeProjection] = []

    def visit(node: Any, inherited_parent_id: str = ""):
        _reject_backend_like_object(node, "scene node")
        projected = _scene_node_from_source(node, parent_id=inherited_parent_id)
        if not projected.parent_id and inherited_parent_id:
            projected = SceneNodeProjection(
                node_id=projected.node_id,
                parent_id=inherited_parent_id,
                node_type=projected.node_type,
                display_name=projected.display_name,
                visible=projected.visible,
                selectable=projected.selectable,
                bounding_box=projected.bounding_box,
                transform=projected.transform,
                display_metadata=projected.display_metadata,
                source_reference=projected.source_reference,
            )
        result.append(projected)
        children = _get_value(node, "children", _as_dict(node).get("children", ())) or ()
        for child in children:
            visit(child, projected.node_id or inherited_parent_id)

    if isinstance(source, (list, tuple)):
        for node in source:
            if isinstance(node, tuple) and len(node) == 2 and not isinstance(node[0], (str, bytes)):
                visit(node[0], str(node[1] or parent_id))
            else:
                visit(node, parent_id)
    else:
        for node in _iter_scene_nodes(source):
            visit(node, parent_id)

    return tuple(result)


def _union_bounds(nodes: tuple[SceneNodeProjection, ...]) -> SceneBoundsProjection:
    if not nodes:
        return SceneBoundsProjection()
    min_x = min(node.bounding_box.minimum[0] for node in nodes)
    min_y = min(node.bounding_box.minimum[1] for node in nodes)
    min_z = min(node.bounding_box.minimum[2] for node in nodes)
    max_x = max(node.bounding_box.maximum[0] for node in nodes)
    max_y = max(node.bounding_box.maximum[1] for node in nodes)
    max_z = max(node.bounding_box.maximum[2] for node in nodes)
    return SceneBoundsProjection(
        minimum=(min_x, min_y, min_z),
        maximum=(max_x, max_y, max_z),
    )


def _selection_from_source(source: Any, nodes: tuple[SceneNodeProjection, ...]) -> SceneSelectionProjection:
    data = _as_dict(source)
    selection = _get_value(source, "selection", data.get("selection", None))
    if selection is not None and selection is not source:
        return _selection_from_source(selection, nodes)

    selected_node_id = _ensure_str(
        str(_get_value(source, "selected_node_id", data.get("selected_node_id", data.get("selected_node", ""))) or ""),
        "selected_node_id",
    )
    if not selected_node_id:
        selected_node_id = _ensure_str(str(_get_value(source, "highlight_target", data.get("highlight_target", "")) or ""), "selected_node_id")
    selected_node = next((node for node in nodes if node.node_id == selected_node_id), None)
    display_name = ""
    node_type = ""
    if selected_node is not None:
        display_name = selected_node.display_name
        node_type = selected_node.node_type
    else:
        display_name = _ensure_str(str(_get_value(source, "display_name", data.get("display_name", "")) or ""), "display_name")
        node_type = _ensure_str(str(_get_value(source, "selected_node_type", data.get("selected_node_type", "")) or ""), "node_type")
    return SceneSelectionProjection(
        selected_node_id=selected_node_id,
        display_name=display_name,
        node_type=node_type,
        highlight_target=_ensure_str(str(_get_value(source, "highlight_target", data.get("highlight_target", selected_node_id)) or selected_node_id), "highlight_target"),
        source_reference=_ensure_str(str(_get_value(source, "source_reference", data.get("source_reference", "")) or ""), "source_reference"),
        warnings=_get_value(source, "warnings", data.get("warnings", ())) or (),
    )


def build_scene_projection(
    source: Any = None,
    *,
    selected_node_id: str = "",
    highlight_target: str = "",
    representation_status: str = "",
    warnings: Iterable[str] | None = None,
    source_reference: str = "",
) -> SceneProjection:
    if source is None:
        return SceneProjection(
            scene_available=False,
            nodes=(),
            bounds=SceneBoundsProjection(),
            selection=SceneSelectionProjection(),
            highlight_target=_ensure_str(highlight_target, "highlight_target"),
            representation_status=representation_status or "Unavailable",
            warnings=tuple(warnings or ()),
            source_reference=source_reference,
            node_count=0,
        )
    if isinstance(source, SceneProjection):
        return source
    if isinstance(source, Mapping) and "scene_projection" in source:
        return build_scene_projection(
            source.get("scene_projection"),
            selected_node_id=selected_node_id or _ensure_str(str(source.get("selected_node_id", "") or ""), "selected_node_id"),
            highlight_target=highlight_target or _ensure_str(str(source.get("highlight_target", "") or ""), "highlight_target"),
            representation_status=representation_status or _ensure_str(str(source.get("representation_status", "") or ""), "representation_status"),
            warnings=warnings if warnings is not None else source.get("warnings", ()),
            source_reference=source_reference or _ensure_str(str(source.get("source_reference", "") or ""), "source_reference"),
        )

    data = _as_dict(source)
    if "scene_graph" in data:
        source = data["scene_graph"]
        data = _as_dict(source)

    node_sources = data.get("nodes", None)
    if node_sources is None:
        node_sources = _iter_scene_nodes(source)
    if isinstance(node_sources, Mapping):
        node_sources = tuple(node_sources.values())
    nodes = _flatten_scene_nodes(node_sources or source)
    node_count = len(nodes)
    bounds = _union_bounds(nodes)
    selection = _selection_from_source(
        {
            **data,
            "selected_node_id": selected_node_id or data.get("selected_node_id", ""),
            "highlight_target": highlight_target or data.get("highlight_target", ""),
            "warnings": warnings if warnings is not None else data.get("warnings", ()),
            "source_reference": source_reference or data.get("source_reference", ""),
        },
        nodes,
    )
    selected_node = selection.selected_node_id or selected_node_id or selection.highlight_target
    if not representation_status:
        representation_status = _ensure_str(str(data.get("representation_status", "") or ""), "representation_status")
    if not representation_status:
        representation_status = "Ready" if node_count else "Unavailable"
    scene_available = bool(node_count)
    if not source_reference:
        source_reference = _ensure_str(str(data.get("source_reference", "") or ""), "source_reference")
    return SceneProjection(
        scene_available=scene_available,
        nodes=nodes,
        bounds=bounds,
        selection=selection,
        highlight_target=_ensure_str(str(highlight_target or selection.highlight_target or selected_node or ""), "highlight_target"),
        representation_status=representation_status,
        warnings=tuple(_ensure_str(str(warning), "warnings") for warning in (warnings or data.get("warnings", ()) or ())),
        source_reference=source_reference,
        node_count=node_count,
    )


__all__ = [
    "SceneBoundsProjection",
    "SceneNodeProjection",
    "SceneSelectionProjection",
    "SceneProjection",
    "build_scene_projection",
]
