from __future__ import annotations

from dataclasses import dataclass, field


def _ensure_str(value, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    return value


def _ensure_bool(value, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be a bool")
    return value


def _ensure_instance_tuple(value, field_name: str, expected_type):
    if value is None:
        return ()
    items = []
    for item in value:
        if not isinstance(item, expected_type):
            raise TypeError(f"{field_name} must contain {expected_type.__name__} instances")
        items.append(item)
    return tuple(items)


def _ensure_string_pairs(value, field_name: str) -> tuple[tuple[str, str], ...]:
    if value is None:
        return ()
    pairs = []
    for item in value:
        if not isinstance(item, tuple) or len(item) != 2:
            raise TypeError(f"{field_name} must contain 2-tuples")
        key, pair_value = item
        pairs.append((_ensure_str(key, f"{field_name}.key"), _ensure_str(pair_value, f"{field_name}.value")))
    return tuple(pairs)


def _ensure_string_tuple(value, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (_ensure_str(value, field_name),)
    return tuple(_ensure_str(item, field_name) for item in value)


@dataclass(frozen=True)
class ProjectTreeNodeReadModel:
    node_id: str = ""
    parent_id: str = ""
    node_type: str = ""
    label: str = ""
    state: str = ""
    is_supported: bool = True
    is_stale: bool = False
    children: tuple["ProjectTreeNodeReadModel", ...] = field(default_factory=tuple)

    def __post_init__(self):
        object.__setattr__(self, "node_id", _ensure_str(self.node_id, "node_id"))
        object.__setattr__(self, "parent_id", _ensure_str(self.parent_id, "parent_id"))
        object.__setattr__(self, "node_type", _ensure_str(self.node_type, "node_type"))
        object.__setattr__(self, "label", _ensure_str(self.label, "label"))
        object.__setattr__(self, "state", _ensure_str(self.state, "state"))
        object.__setattr__(self, "is_supported", _ensure_bool(self.is_supported, "is_supported"))
        object.__setattr__(self, "is_stale", _ensure_bool(self.is_stale, "is_stale"))
        object.__setattr__(
            self,
            "children",
            _ensure_instance_tuple(self.children, "children", ProjectTreeNodeReadModel),
        )


@dataclass(frozen=True)
class ProjectTreeReadModel:
    root_nodes: tuple[ProjectTreeNodeReadModel, ...] = field(default_factory=tuple)
    selected_node_id: str = ""
    expanded_node_ids: tuple[str, ...] = field(default_factory=tuple)
    unsupported_node_ids: tuple[str, ...] = field(default_factory=tuple)
    stale_node_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        object.__setattr__(
            self,
            "root_nodes",
            _ensure_instance_tuple(self.root_nodes, "root_nodes", ProjectTreeNodeReadModel),
        )
        object.__setattr__(self, "selected_node_id", _ensure_str(self.selected_node_id, "selected_node_id"))
        object.__setattr__(self, "expanded_node_ids", tuple(_ensure_str(node_id, "expanded_node_ids") for node_id in (self.expanded_node_ids or ())))
        object.__setattr__(self, "unsupported_node_ids", tuple(_ensure_str(node_id, "unsupported_node_ids") for node_id in (self.unsupported_node_ids or ())))
        object.__setattr__(self, "stale_node_ids", tuple(_ensure_str(node_id, "stale_node_ids") for node_id in (self.stale_node_ids or ())))


@dataclass(frozen=True)
class InspectorFieldReadModel:
    name: str = ""
    label: str = ""
    value: str = ""
    unit: str = ""
    editable: bool = False
    source_reference: str = ""
    group: str = ""

    def __post_init__(self):
        object.__setattr__(self, "name", _ensure_str(self.name, "name"))
        object.__setattr__(self, "label", _ensure_str(self.label, "label"))
        object.__setattr__(self, "value", _ensure_str(self.value, "value"))
        object.__setattr__(self, "unit", _ensure_str(self.unit, "unit"))
        object.__setattr__(self, "editable", _ensure_bool(self.editable, "editable"))
        object.__setattr__(self, "source_reference", _ensure_str(self.source_reference, "source_reference"))
        object.__setattr__(self, "group", _ensure_str(self.group, "group"))


@dataclass(frozen=True)
class InspectorReadModel:
    selection_id: str = ""
    selection_type: str = "NONE"
    display_name: str = ""
    fields: tuple[InspectorFieldReadModel, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    source_reference: str = ""
    unsupported: bool = False
    unsupported_reason: str = ""
    suggested_action: str = ""
    stale: bool = False

    def __post_init__(self):
        object.__setattr__(self, "selection_id", _ensure_str(self.selection_id, "selection_id"))
        object.__setattr__(self, "selection_type", _ensure_str(self.selection_type, "selection_type"))
        object.__setattr__(self, "display_name", _ensure_str(self.display_name, "display_name"))
        object.__setattr__(
            self,
            "fields",
            _ensure_instance_tuple(self.fields, "fields", InspectorFieldReadModel),
        )
        object.__setattr__(self, "warnings", tuple(_ensure_str(warning, "warnings") for warning in (self.warnings or ())))
        object.__setattr__(self, "source_reference", _ensure_str(self.source_reference, "source_reference"))
        object.__setattr__(self, "unsupported", _ensure_bool(self.unsupported, "unsupported"))
        object.__setattr__(self, "unsupported_reason", _ensure_str(self.unsupported_reason, "unsupported_reason"))
        object.__setattr__(self, "suggested_action", _ensure_str(self.suggested_action, "suggested_action"))
        object.__setattr__(self, "stale", _ensure_bool(self.stale, "stale"))


@dataclass(frozen=True)
class PreviewItemReadModel:
    item_id: str = ""
    item_type: str = ""
    label: str = ""
    visible: bool = True
    selected: bool = False
    display_metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    source_reference: str = ""
    representation: str = ""

    def __post_init__(self):
        object.__setattr__(self, "item_id", _ensure_str(self.item_id, "item_id"))
        object.__setattr__(self, "item_type", _ensure_str(self.item_type, "item_type"))
        object.__setattr__(self, "label", _ensure_str(self.label, "label"))
        object.__setattr__(self, "visible", _ensure_bool(self.visible, "visible"))
        object.__setattr__(self, "selected", _ensure_bool(self.selected, "selected"))
        object.__setattr__(self, "display_metadata", _ensure_string_pairs(self.display_metadata, "display_metadata"))
        object.__setattr__(self, "source_reference", _ensure_str(self.source_reference, "source_reference"))
        object.__setattr__(self, "representation", _ensure_str(self.representation, "representation"))


@dataclass(frozen=True)
class PreviewReadModel:
    preview_title: str = ""
    preview_mode: str = "Customer View"
    preview_state: str = "Unavailable"
    items: tuple[PreviewItemReadModel, ...] = field(default_factory=tuple)
    highlighted_item_id: str = ""
    highlighted_item_type: str = ""
    current_family: str = ""
    viewport_message: str = ""
    available_representations: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    stale: bool = False
    unsupported_reason: str = ""

    def __post_init__(self):
        object.__setattr__(self, "preview_title", _ensure_str(self.preview_title, "preview_title"))
        object.__setattr__(self, "preview_mode", _ensure_str(self.preview_mode, "preview_mode"))
        object.__setattr__(self, "preview_state", _ensure_str(self.preview_state, "preview_state"))
        object.__setattr__(
            self,
            "items",
            _ensure_instance_tuple(self.items, "items", PreviewItemReadModel),
        )
        object.__setattr__(self, "highlighted_item_id", _ensure_str(self.highlighted_item_id, "highlighted_item_id"))
        object.__setattr__(self, "highlighted_item_type", _ensure_str(self.highlighted_item_type, "highlighted_item_type"))
        object.__setattr__(self, "current_family", _ensure_str(self.current_family, "current_family"))
        object.__setattr__(self, "viewport_message", _ensure_str(self.viewport_message, "viewport_message"))
        object.__setattr__(self, "available_representations", _ensure_string_tuple(self.available_representations, "available_representations"))
        object.__setattr__(self, "warnings", tuple(_ensure_str(warning, "warnings") for warning in (self.warnings or ())))
        object.__setattr__(self, "stale", _ensure_bool(self.stale, "stale"))
        object.__setattr__(self, "unsupported_reason", _ensure_str(self.unsupported_reason, "unsupported_reason"))


@dataclass(frozen=True)
class MessageReadModel:
    message_id: str = ""
    severity: str = "INFO"
    category: str = ""
    text: str = ""
    source_reference: str = ""
    acknowledged: bool = False
    blocking: bool = False

    def __post_init__(self):
        object.__setattr__(self, "message_id", _ensure_str(self.message_id, "message_id"))
        object.__setattr__(self, "severity", _ensure_str(self.severity, "severity"))
        object.__setattr__(self, "category", _ensure_str(self.category, "category"))
        object.__setattr__(self, "text", _ensure_str(self.text, "text"))
        object.__setattr__(self, "source_reference", _ensure_str(self.source_reference, "source_reference"))
        object.__setattr__(self, "acknowledged", _ensure_bool(self.acknowledged, "acknowledged"))
        object.__setattr__(self, "blocking", _ensure_bool(self.blocking, "blocking"))


@dataclass(frozen=True)
class MessageCenterReadModel:
    messages: tuple[MessageReadModel, ...] = field(default_factory=tuple)
    highest_severity: str = "INFO"
    has_blockers: bool = False
    has_stale_outputs: bool = False

    def __post_init__(self):
        object.__setattr__(
            self,
            "messages",
            _ensure_instance_tuple(self.messages, "messages", MessageReadModel),
        )
        object.__setattr__(self, "highest_severity", _ensure_str(self.highest_severity, "highest_severity"))
        object.__setattr__(self, "has_blockers", _ensure_bool(self.has_blockers, "has_blockers"))
        object.__setattr__(self, "has_stale_outputs", _ensure_bool(self.has_stale_outputs, "has_stale_outputs"))


@dataclass(frozen=True)
class ReviewSectionReadModel:
    section_name: str = ""
    rows: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    source_reference: str = ""

    def __post_init__(self):
        object.__setattr__(self, "section_name", _ensure_str(self.section_name, "section_name"))
        object.__setattr__(self, "rows", _ensure_string_pairs(self.rows, "rows"))
        object.__setattr__(self, "warnings", tuple(_ensure_str(warning, "warnings") for warning in (self.warnings or ())))
        object.__setattr__(self, "source_reference", _ensure_str(self.source_reference, "source_reference"))


@dataclass(frozen=True)
class ReviewPanelReadModel:
    panel_name: str = ""
    sections: tuple[ReviewSectionReadModel, ...] = field(default_factory=tuple)
    stale: bool = False
    available: bool = True

    def __post_init__(self):
        object.__setattr__(self, "panel_name", _ensure_str(self.panel_name, "panel_name"))
        object.__setattr__(
            self,
            "sections",
            _ensure_instance_tuple(self.sections, "sections", ReviewSectionReadModel),
        )
        object.__setattr__(self, "stale", _ensure_bool(self.stale, "stale"))
        object.__setattr__(self, "available", _ensure_bool(self.available, "available"))


def empty_project_tree_read_model() -> ProjectTreeReadModel:
    return ProjectTreeReadModel()


def empty_inspector_read_model() -> InspectorReadModel:
    return InspectorReadModel()


def empty_preview_read_model() -> PreviewReadModel:
    return PreviewReadModel()


def empty_message_center_read_model() -> MessageCenterReadModel:
    return MessageCenterReadModel()


def empty_review_panel_read_models(
    panel_names: tuple[str, ...] = (
        "Validation",
        "Manufacturing",
        "Cost",
        "Commercial",
        "Release",
    ),
) -> tuple[ReviewPanelReadModel, ...]:
    return tuple(ReviewPanelReadModel(panel_name=panel_name) for panel_name in panel_names)


__all__ = [
    "ProjectTreeReadModel",
    "ProjectTreeNodeReadModel",
    "InspectorReadModel",
    "InspectorFieldReadModel",
    "PreviewReadModel",
    "PreviewItemReadModel",
    "MessageCenterReadModel",
    "MessageReadModel",
    "ReviewPanelReadModel",
    "ReviewSectionReadModel",
    "empty_project_tree_read_model",
    "empty_inspector_read_model",
    "empty_preview_read_model",
    "empty_message_center_read_model",
    "empty_review_panel_read_models",
]
