from __future__ import annotations

from dataclasses import dataclass, field

from core.qt_compat import QtWidgets

WORKSPACE_AREAS = (
    "Dashboard",
    "Projects",
    "Customers",
    "Product Families",
    "Materials / Hardware",
    "Manufacturing",
    "Cost",
    "Commercial",
    "Factory Release",
    "Settings",
)

REVIEW_PANEL_NAMES = (
    "Validation",
    "Manufacturing",
    "Cost",
    "Commercial",
    "Release",
)

PREVIEW_MODES = (
    "Customer View",
    "Design View",
    "Manufacturing Detail View",
    "Assembly View",
    "Cost View",
    "Quality Review View",
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


@dataclass(frozen=True)
class ConfiguratorV2ShellModel:
    workspace_areas: tuple[str, ...] = WORKSPACE_AREAS
    project_tree_nodes: tuple[str, ...] = (
        "Customer",
        "Project",
        "Room",
        "Wall",
        "Product / Cabinet",
        "Documents",
    )
    preview_modes: tuple[str, ...] = PREVIEW_MODES
    review_panels: tuple[str, ...] = REVIEW_PANEL_NAMES
    action_names: tuple[str, ...] = ACTION_NAMES
    message_categories: tuple[str, ...] = MESSAGE_CATEGORIES


def _safe_set(obj, name, value):
    if hasattr(obj, name):
        getattr(obj, name)(value) if callable(getattr(obj, name)) else None


class _ShellFrame(QtWidgets.QFrame):
    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        if hasattr(self, "setObjectName"):
            self.setObjectName(title.replace(" ", "_").lower())

        layout = QtWidgets.QVBoxLayout(self)
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


class NavigationPanel(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Global Navigation",
            "Top-level product areas for the Configurator workspace.",
            parent=parent,
        )
        self.area_buttons: dict[str, object] = {}
        for area in WORKSPACE_AREAS:
            button = QtWidgets.QPushButton(area)
            if hasattr(button, "setEnabled"):
                button.setEnabled(False)
            self.body_layout.addWidget(button)
            self.area_buttons[area] = button


class ProjectTreePanel(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Project Tree",
            "Customer, project, room, wall, cabinet, and document hierarchy.",
            parent=parent,
        )
        self.tree_nodes: tuple[str, ...] = ConfiguratorV2ShellModel().project_tree_nodes
        for index, node_name in enumerate(self.tree_nodes, start=1):
            label = QtWidgets.QLabel(f"{index}. {node_name}")
            self.body_layout.addWidget(label)


class PreviewPanel(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Preview",
            "Live preview placeholder backed by SceneGraph and FreeCAD later.",
            parent=parent,
        )
        self.preview_mode_selector = QtWidgets.QComboBox()
        for mode in PREVIEW_MODES:
            self.preview_mode_selector.addItem(mode)
        self.body_layout.addWidget(self.preview_mode_selector)
        self.preview_placeholder = QtWidgets.QLabel("Live preview placeholder")
        if hasattr(self.preview_placeholder, "setMinimumHeight"):
            self.preview_placeholder.setMinimumHeight(240)
        self.body_layout.addWidget(self.preview_placeholder)


class InspectorPanel(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Inspector",
            "Selected object properties and draft-editable values.",
            parent=parent,
        )
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
            form.addRow(label_text, QtWidgets.QLabel("No selection"))
        self.body_layout.addLayout(form)


class ReviewPanels(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Review Panels",
            "Validation, manufacturing, cost, commercial, and release evidence.",
            parent=parent,
        )
        self.tabs = QtWidgets.QTabWidget()
        self.review_widgets: dict[str, object] = {}
        for panel_name in REVIEW_PANEL_NAMES:
            widget = _ShellFrame(
                panel_name,
                f"Read-only {panel_name.lower()} evidence.",
            )
            self.tabs.addTab(widget, panel_name)
            self.review_widgets[panel_name] = widget
        self.body_layout.addWidget(self.tabs)


class MessageCenterPanel(_ShellFrame):
    def __init__(self, parent=None):
        super().__init__(
            "Message Center",
            "Persistent blockers, warnings, stale data, and system errors.",
            parent=parent,
        )
        self.message_list = QtWidgets.QLabel(
            "No messages. Backend warnings and blockers will appear here."
        )
        if hasattr(self.message_list, "setWordWrap"):
            self.message_list.setWordWrap(True)
        self.body_layout.addWidget(self.message_list)

        categories = QtWidgets.QLabel(
            " | ".join(MESSAGE_CATEGORIES)
        )
        if hasattr(categories, "setWordWrap"):
            categories.setWordWrap(True)
        self.body_layout.addWidget(categories)


class ActionBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.action_buttons: dict[str, object] = {}
        layout = QtWidgets.QHBoxLayout(self)
        for action_name in ACTION_NAMES:
            button = QtWidgets.QPushButton(action_name)
            if hasattr(button, "setEnabled"):
                button.setEnabled(False)
            layout.addWidget(button)
            self.action_buttons[action_name] = button


class ConfiguratorV2Workspace(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shell_model = ConfiguratorV2ShellModel()
        self.workspace_areas = self.shell_model.workspace_areas
        self.action_names = self.shell_model.action_names
        self.preview_modes = self.shell_model.preview_modes
        self.review_panel_names = self.shell_model.review_panels
        self.message_categories = self.shell_model.message_categories

        root_layout = QtWidgets.QVBoxLayout(self)
        content_layout = QtWidgets.QHBoxLayout()

        left_column = QtWidgets.QVBoxLayout()
        self.navigation_panel = NavigationPanel()
        self.project_tree_panel = ProjectTreePanel()
        left_column.addWidget(self.navigation_panel)
        left_column.addWidget(self.project_tree_panel)
        content_layout.addLayout(left_column)

        center_column = QtWidgets.QVBoxLayout()
        self.preview_panel = PreviewPanel()
        center_column.addWidget(self.preview_panel)
        content_layout.addLayout(center_column)

        right_column = QtWidgets.QVBoxLayout()
        self.inspector_panel = InspectorPanel()
        self.review_panels = ReviewPanels()
        right_column.addWidget(self.inspector_panel)
        right_column.addWidget(self.review_panels)
        content_layout.addLayout(right_column)

        root_layout.addLayout(content_layout)

        self.message_center = MessageCenterPanel()
        root_layout.addWidget(self.message_center)

        self.action_bar = ActionBar()
        root_layout.addWidget(self.action_bar)


def create_configurator_v2_workspace(parent=None) -> ConfiguratorV2Workspace:
    return ConfiguratorV2Workspace(parent=parent)
