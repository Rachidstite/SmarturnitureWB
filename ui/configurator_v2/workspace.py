from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.qt_compat import QtWidgets
from .read_models import (
    InspectorReadModel,
    MessageCenterReadModel,
    PreviewReadModel,
    ProjectTreeReadModel,
    ReviewPanelReadModel,
    empty_inspector_read_model,
    empty_message_center_read_model,
    empty_preview_read_model,
    empty_project_tree_read_model,
    empty_review_panel_read_models,
)

NAVIGATION_ENTRIES = (
    "Dashboard",
    "Projects",
    "Customers",
    "Product Families",
    "Configurator",
    "Manufacturing",
    "Cost",
    "Commercial",
    "Factory Release",
    "Settings",
)

WORKSPACE_AREAS = NAVIGATION_ENTRIES

PROJECT_TREE_NODES = (
    "Customer",
    "Project",
    "Room",
    "Wall",
    "Product / Cabinet",
    "Documents",
)

PRODUCT_STATES = (
    "Draft",
    "Configured",
    "Validated",
    "Manufacturing Ready",
    "Cost Reviewed",
    "Commercial Approved",
    "Released",
    "Manufactured",
)

PREVIEW_MODES = (
    "Customer View",
    "Design View",
    "Manufacturing Detail View",
    "Assembly View",
    "Cost View",
    "Quality Review View",
)

REVIEW_PANEL_NAMES = (
    "Validation",
    "Manufacturing",
    "Cost",
    "Commercial",
    "Release",
)

ACTION_NAMES = (
    "Save Draft",
    "Refresh Preview",
    "Validate",
    "Generate Manufacturing",
    "Review Cost",
    "Generate Quotation",
    "Approve Release",
    "Export Production Documents",
)

MESSAGE_SEVERITIES = ("BLOCKER", "WARNING", "INFO", "STALE", "UNSUPPORTED")

MESSAGE_CATEGORIES = (
    "Blocking validation errors",
    "Non-blocking warnings",
    "Manufacturing blockers",
    "Commercial warnings",
    "Release blockers",
    "Stale output warnings",
    "Unsupported product family warnings",
    "System errors",
)

SELECTION_TYPES = (
    "NONE",
    "PROJECT",
    "ROOM",
    "WALL",
    "PRODUCT",
    "CABINET",
    "PART",
    "PANEL",
    "DOOR",
    "DRAWER",
    "SHELF",
    "DIVIDER",
    "HARDWARE",
    "DOCUMENT",
)


@dataclass(frozen=True)
class ConfiguratorV2ShellModel:
    navigation_entries: tuple[str, ...] = NAVIGATION_ENTRIES
    project_tree_nodes: tuple[str, ...] = PROJECT_TREE_NODES
    product_states: tuple[str, ...] = PRODUCT_STATES
    preview_modes: tuple[str, ...] = PREVIEW_MODES
    review_panels: tuple[str, ...] = REVIEW_PANEL_NAMES
    action_names: tuple[str, ...] = ACTION_NAMES
    message_categories: tuple[str, ...] = MESSAGE_CATEGORIES
    message_severities: tuple[str, ...] = MESSAGE_SEVERITIES
    selection_types: tuple[str, ...] = SELECTION_TYPES


@dataclass(frozen=True)
class ConfiguratorSelection:
    selection_type: str = "NONE"
    selection_id: str = ""
    display_name: str = ""
    source_region: str = ""
    metadata: dict[str, Any] | None = None


@dataclass
class ConfiguratorV2ServiceBindings:
    project_application_service: Any | None = None
    engineering_application_service: Any | None = None
    manufacturing_application_service: Any | None = None


def _frame_layout(widget):
    layout = QtWidgets.QVBoxLayout(widget)
    if hasattr(layout, "setContentsMargins"):
        layout.setContentsMargins(8, 8, 8, 8)
    return layout


class _ShellFrame(QtWidgets.QFrame):
    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        if hasattr(self, "setObjectName"):
            self.setObjectName(title.replace(" ", "_").lower())

        layout = _frame_layout(self)
        title_label = QtWidgets.QLabel(title)
        if hasattr(title_label, "setObjectName"):
            title_label.setObjectName(f"{self.objectName()}_title")
        layout.addWidget(title_label)

        if description:
            description_label = QtWidgets.QLabel(description)
            if hasattr(description_label, "setWordWrap"):
                description_label.setWordWrap(True)
            layout.addWidget(description_label)

        self.body_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self.body_layout)


class NavigationEntry:
    def __init__(self, name: str, *, enabled: bool = True, active: bool = False):
        self.name = name
        self.enabled = enabled
        self.active = active
        self.button = None


class GlobalNavigationRegion(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Global Navigation",
            "Top-level product areas for the Configurator workspace.",
            parent=parent,
        )
        self.navigation_entries: dict[str, NavigationEntry] = {
            entry: NavigationEntry(
                entry,
                enabled=True,
                active=(entry == "Dashboard"),
            )
            for entry in NAVIGATION_ENTRIES
        }
        self.navigation_buttons: dict[str, object] = {}
        for entry_name, entry in self.navigation_entries.items():
            button = QtWidgets.QPushButton(entry_name)
            if hasattr(button, "setEnabled"):
                button.setEnabled(entry.enabled)
            if hasattr(button, "setCheckable"):
                button.setCheckable(True)
            if hasattr(button, "setChecked"):
                button.setChecked(entry.active)
            self.body_layout.addWidget(button)
            entry.button = button
            self.navigation_buttons[entry_name] = button


class ProjectTreeRegion(_ShellFrame):
    def __init__(self, parent=None, on_select=None):
        super().__init__(
            "Project Tree",
            "Customer, project, room, wall, cabinet, and document hierarchy.",
            parent=parent,
        )
        self.on_select = on_select
        self.selected_node = None
        self.tree_nodes: tuple[str, ...] = ConfiguratorV2ShellModel().project_tree_nodes
        self.read_model = empty_project_tree_read_model()
        self.selected_node_id = ""
        self.node_labels: dict[str, object] = {}
        self.node_metadata: dict[str, dict[str, str]] = {}
        self.render_rows: list[str] = []
        self._node_lookup: dict[str, object] = {}
        self.body_layout.addWidget(QtWidgets.QLabel("No project tree loaded"))

    def _flatten_nodes(self, nodes):
        for node in nodes or ():
            yield node
            yield from self._flatten_nodes(getattr(node, "children", ()) or ())

    def _rebuild_render_state(self):
        if hasattr(self.body_layout, "items"):
            self.body_layout.items = []
        self.node_labels.clear()
        self.node_metadata.clear()
        self.render_rows = []
        self._node_lookup = {}

        if not getattr(self.read_model, "root_nodes", None):
            self.render_rows.append("No project tree loaded")
            return

        def visit(node, depth=0):
            self._node_lookup[node.node_id] = node
            metadata_bits = [
                f"state={node.state}" if node.state else "",
                "supported" if node.is_supported else "unsupported",
                "stale" if node.is_stale else "",
            ]
            metadata_text = ", ".join(bit for bit in metadata_bits if bit)
            row_text = f"{'  ' * depth}{node.label}"
            if node.node_id == self.selected_node_id:
                row_text = f"> {row_text}"
            if metadata_text:
                row_text = f"{row_text} [{metadata_text}]"
            self.render_rows.append(row_text)
            label = QtWidgets.QLabel(row_text)
            self.body_layout.addWidget(label)
            self.node_labels[node.node_id] = label
            self.node_metadata[node.node_id] = {
                "state": node.state,
                "is_supported": str(node.is_supported),
                "is_stale": str(node.is_stale),
                "label": node.label,
                "node_type": node.node_type,
                "parent_id": node.parent_id,
            }
            for child in node.children:
                visit(child, depth + 1)

        for root_node in self.read_model.root_nodes:
            visit(root_node)

    def set_read_model(self, read_model: ProjectTreeReadModel):
        self.read_model = read_model or empty_project_tree_read_model()
        self.selected_node_id = getattr(self.read_model, "selected_node_id", "") or ""
        self.selected_node = self.selected_node_id or None
        self._rebuild_render_state()

    def select_node(self, node_id: str):
        self.selected_node = node_id
        self.selected_node_id = node_id
        node = self._node_lookup.get(node_id)
        if node is None:
            selection = ConfiguratorSelection(
                selection_type="PROJECT",
                selection_id=node_id,
                display_name=node_id,
                source_region="ProjectTreeRegion",
                metadata={"tree_node": node_id},
            )
        else:
            selection = ConfiguratorSelection(
                selection_type=(node.node_type or "PROJECT").upper(),
                selection_id=node.node_id,
                display_name=node.label or node.node_id,
                source_region="ProjectTreeRegion",
                metadata={
                    "tree_node": node.node_id,
                    "state": node.state,
                    "is_supported": str(node.is_supported),
                    "is_stale": str(node.is_stale),
                    "parent_id": node.parent_id,
                },
            )
        if callable(self.on_select):
            self.on_select(selection)


class PreviewRegion(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Preview",
            "Live preview placeholder backed by SceneGraph and FreeCAD later.",
            parent=parent,
        )
        self.preview_modes: tuple[str, ...] = ConfiguratorV2ShellModel().preview_modes
        self.preview_mode_selector = QtWidgets.QComboBox()
        for mode in self.preview_modes:
            self.preview_mode_selector.addItem(mode)
        self.body_layout.addWidget(self.preview_mode_selector)
        self.preview_placeholder = QtWidgets.QLabel("Live preview placeholder")
        if hasattr(self.preview_placeholder, "setMinimumHeight"):
            self.preview_placeholder.setMinimumHeight(240)
        self.body_layout.addWidget(self.preview_placeholder)
        self.highlighted_selection_id = ""
        self.highlighted_selection_type = "NONE"

    def set_selection_highlight(self, selection: ConfiguratorSelection):
        self.highlighted_selection_id = selection.selection_id
        self.highlighted_selection_type = selection.selection_type


class ProductContextRegion(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Project Context",
            "Display-only current customer, project, family, product, and state.",
            parent=parent,
        )
        self.current_customer = None
        self.current_project = None
        self.current_product_family = None
        self.current_product = None
        self.current_product_state = "Draft"
        self.context_labels: dict[str, object] = {}
        for label_text in (
            "Current Customer",
            "Current Project",
            "Current Product Family",
            "Current Product",
            "Current Product State",
        ):
            value_label = QtWidgets.QLabel("Not selected")
            self.body_layout.addWidget(QtWidgets.QLabel(label_text))
            self.body_layout.addWidget(value_label)
            self.context_labels[label_text] = value_label
        self.set_context_state(current_state=self.current_product_state)

    def set_context_state(
        self,
        *,
        current_customer=None,
        current_project=None,
        current_product_family=None,
        current_product=None,
        current_state=None,
    ):
        self.current_customer = current_customer
        self.current_project = current_project
        self.current_product_family = current_product_family
        self.current_product = current_product
        if current_state is not None:
            self.current_product_state = current_state

        values = {
            "Current Customer": current_customer,
            "Current Project": current_project,
            "Current Product Family": current_product_family,
            "Current Product": current_product,
            "Current Product State": self.current_product_state,
        }
        for label_text, value in values.items():
            widget = self.context_labels.get(label_text)
            if widget is not None and hasattr(widget, "setText"):
                widget.setText(str(value) if value is not None else "Not selected")


class ProductStateIndicator(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Product State",
            "Display-only indicator for the ADR-0015 state model.",
            parent=parent,
        )
        self.states = ConfiguratorV2ShellModel().product_states
        self.state_labels: dict[str, object] = {}
        self.current_state = "Draft"
        for state_name in self.states:
            label = QtWidgets.QLabel(state_name)
            self.body_layout.addWidget(label)
            self.state_labels[state_name] = label
        self.set_state(self.current_state)

    def set_state(self, state_name: str):
        self.current_state = state_name
        for label_state, widget in self.state_labels.items():
            if hasattr(widget, "setText"):
                prefix = "● " if label_state == state_name else "○ "
                widget.setText(f"{prefix}{label_state}")


class InspectorRegion(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Inspector",
            "Selected object properties and draft-editable values.",
            parent=parent,
        )
        self.selection_type_value = QtWidgets.QLabel("NONE")
        self.display_name_value = QtWidgets.QLabel("Not selected")
        self.selection_id_value = QtWidgets.QLabel("")
        self.source_region_value = QtWidgets.QLabel("")
        self.metadata_value = QtWidgets.QLabel("{}")
        self.body_layout.addWidget(QtWidgets.QLabel("Selection Type"))
        self.body_layout.addWidget(self.selection_type_value)
        self.body_layout.addWidget(QtWidgets.QLabel("Display Name"))
        self.body_layout.addWidget(self.display_name_value)
        self.body_layout.addWidget(QtWidgets.QLabel("Selection ID"))
        self.body_layout.addWidget(self.selection_id_value)
        self.body_layout.addWidget(QtWidgets.QLabel("Source Region"))
        self.body_layout.addWidget(self.source_region_value)
        self.body_layout.addWidget(QtWidgets.QLabel("Metadata"))
        self.body_layout.addWidget(self.metadata_value)
        self.property_rows: dict[str, object] = {}
        form = QtWidgets.QFormLayout()
        for label_text in (
            "Dimensions",
            "Materials",
            "Doors",
            "Drawers",
            "Shelves",
            "Dividers",
            "Hardware",
        ):
            value_widget = QtWidgets.QLabel("No selection")
            form.addRow(label_text, value_widget)
            self.property_rows[label_text] = value_widget
        self.body_layout.addLayout(form)

    def set_selection(self, selection: ConfiguratorSelection):
        self.selection_type_value.setText(selection.selection_type)
        self.display_name_value.setText(selection.display_name or "Not selected")
        self.selection_id_value.setText(selection.selection_id or "")
        self.source_region_value.setText(selection.source_region or "")
        metadata = dict(selection.metadata or {})
        self.metadata_value.setText(
            ", ".join(f"{key}={value}" for key, value in metadata.items())
            if metadata
            else "{}"
        )


class ReviewContainer(_ShellFrame):
    def __init__(self, name: str, parent=None):
        super().__init__(name, f"Read-only {name.lower()} evidence.", parent=parent)
        self.review_name = name
        self.body_layout.addWidget(QtWidgets.QLabel("No report loaded"))


class ReviewRegion(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Review Panels",
            "Validation, manufacturing, cost, commercial, and release evidence.",
            parent=parent,
        )
        self.review_containers: dict[str, ReviewContainer] = {}
        self.tabs = QtWidgets.QTabWidget()
        for panel_name in REVIEW_PANEL_NAMES:
            widget = ReviewContainer(panel_name)
            self.tabs.addTab(widget, panel_name)
            self.review_containers[panel_name] = widget
        self.body_layout.addWidget(self.tabs)


class MessageCenterRegion(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Message Center",
            "Persistent blockers, warnings, stale data, and system errors.",
            parent=parent,
        )
        self.message_severities = ConfiguratorV2ShellModel().message_severities
        self.message_categories = ConfiguratorV2ShellModel().message_categories
        self.message_list = QtWidgets.QLabel(
            "No messages. Backend warnings and blockers will appear here."
        )
        if hasattr(self.message_list, "setWordWrap"):
            self.message_list.setWordWrap(True)
        self.body_layout.addWidget(self.message_list)

        self.severity_legend = QtWidgets.QLabel(" | ".join(self.message_severities))
        if hasattr(self.severity_legend, "setWordWrap"):
            self.severity_legend.setWordWrap(True)
        self.body_layout.addWidget(self.severity_legend)

        self.category_legend = QtWidgets.QLabel(" | ".join(self.message_categories))
        if hasattr(self.category_legend, "setWordWrap"):
            self.category_legend.setWordWrap(True)
        self.body_layout.addWidget(self.category_legend)


class ActionBarRegion(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.action_names = ConfiguratorV2ShellModel().action_names
        self.action_buttons: dict[str, object] = {}
        self.last_placeholder_action: str | None = None
        layout = QtWidgets.QHBoxLayout(self)
        for action_name in self.action_names:
            button = QtWidgets.QPushButton(action_name)
            if hasattr(button, "setEnabled"):
                button.setEnabled(False)
            layout.addWidget(button)
            self.action_buttons[action_name] = button

    def emit_placeholder_action(self, action_name: str):
        if action_name in self.action_buttons:
            self.last_placeholder_action = action_name


class ConfiguratorV2Workspace(QtWidgets.QWidget):
    def __init__(
        self,
        parent=None,
        *,
        service_bindings: ConfiguratorV2ServiceBindings | None = None,
    ):
        super().__init__(parent)
        self.shell_model = ConfiguratorV2ShellModel()
        self.service_bindings = service_bindings or ConfiguratorV2ServiceBindings()

        self.navigation_entries = self.shell_model.navigation_entries
        self.project_tree_nodes = self.shell_model.project_tree_nodes
        self.workspace_areas = self.navigation_entries
        self.product_states = self.shell_model.product_states
        self.action_names = self.shell_model.action_names
        self.preview_modes = self.shell_model.preview_modes
        self.review_panel_names = self.shell_model.review_panels
        self.message_categories = self.shell_model.message_categories
        self.message_severities = self.shell_model.message_severities

        self.current_customer = None
        self.current_project = None
        self.current_product_family = None
        self.current_product = None
        self.current_product_state = "Draft"
        self.current_selection = ConfiguratorSelection()
        self.service_integration = None
        self.project_tree_read_model = empty_project_tree_read_model()
        self.inspector_read_model = empty_inspector_read_model()
        self.preview_read_model = empty_preview_read_model()
        self.message_center_read_model = empty_message_center_read_model()
        self.review_panel_read_models = empty_review_panel_read_models(
            self.review_panel_names
        )

        root_layout = QtWidgets.QVBoxLayout(self)
        content_layout = QtWidgets.QHBoxLayout()

        left_column = QtWidgets.QVBoxLayout()
        self.global_navigation_region = GlobalNavigationRegion()
        self.project_tree_region = ProjectTreeRegion(on_select=self.set_selection)
        left_column.addWidget(self.global_navigation_region)
        left_column.addWidget(self.project_tree_region)
        content_layout.addLayout(left_column)

        center_column = QtWidgets.QVBoxLayout()
        self.preview_region = PreviewRegion()
        center_column.addWidget(self.preview_region)
        content_layout.addLayout(center_column)

        right_column = QtWidgets.QVBoxLayout()
        self.project_context_region = ProductContextRegion()
        self.product_state_indicator = ProductStateIndicator()
        self.inspector_region = InspectorRegion()
        self.review_region = ReviewRegion()
        right_column.addWidget(self.project_context_region)
        right_column.addWidget(self.product_state_indicator)
        right_column.addWidget(self.inspector_region)
        right_column.addWidget(self.review_region)
        content_layout.addLayout(right_column)

        root_layout.addLayout(content_layout)

        self.message_center_region = MessageCenterRegion()
        root_layout.addWidget(self.message_center_region)

        self.action_bar_region = ActionBarRegion()
        root_layout.addWidget(self.action_bar_region)

    def set_project_context(
        self,
        *,
        current_customer=None,
        current_project=None,
        current_product_family=None,
        current_product=None,
        current_state=None,
    ):
        self.current_customer = current_customer
        self.current_project = current_project
        self.current_product_family = current_product_family
        self.current_product = current_product
        if current_state is not None:
            self.current_product_state = current_state
        self.project_context_region.set_context_state(
            current_customer=current_customer,
            current_project=current_project,
            current_product_family=current_product_family,
            current_product=current_product,
            current_state=self.current_product_state,
        )
        self.product_state_indicator.set_state(self.current_product_state)

    def set_selection(self, selection: ConfiguratorSelection | None):
        selection = selection or ConfiguratorSelection()
        self.current_selection = selection
        self.inspector_region.set_selection(selection)
        self.preview_region.set_selection_highlight(selection)

    def clear_selection(self):
        self.set_selection(ConfiguratorSelection())

    def attach_service_integration(self, service_integration):
        self.service_integration = service_integration

    def set_project_tree_read_model(self, read_model: ProjectTreeReadModel):
        self.project_tree_read_model = read_model
        self.project_tree_region.set_read_model(read_model)

    def set_inspector_read_model(self, read_model: InspectorReadModel):
        self.inspector_read_model = read_model

    def set_preview_read_model(self, read_model: PreviewReadModel):
        self.preview_read_model = read_model

    def set_message_center_read_model(self, read_model: MessageCenterReadModel):
        self.message_center_read_model = read_model

    def set_review_panel_read_models(
        self,
        read_models: tuple[ReviewPanelReadModel, ...],
    ):
        self.review_panel_read_models = tuple(read_models or ())


def create_configurator_v2_workspace(
    parent=None,
    *,
    service_bindings: ConfiguratorV2ServiceBindings | None = None,
) -> ConfiguratorV2Workspace:
    return ConfiguratorV2Workspace(parent=parent, service_bindings=service_bindings)
