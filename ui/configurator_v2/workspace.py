from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.qt_compat import QtWidgets
from .engineering_state import ActiveEngineeringState
from .read_models import (
    InspectorFieldReadModel,
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
from .projection_adapters import build_inspector_read_model, build_preview_read_model, enrich_inspector_source_with_specification
from .furniture_visual_styles import (
    FurnitureVisualStyle,
    apply_furniture_visual_styles,
    style_summary_label,
)
from .interactive_components import (
    INTERACTIVE_STATES,
    InteractiveVisualComponent,
    build_interactive_visual_components,
    count_active_interactions,
    interaction_summary_label,
)
from .presentation_synchronization import (
    SynchronizedPresentation,
    synchronize_presentation,
)
from .visual_components import VisualComponent

from factory_dashboard import FactoryDashboardReadModel

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

INSPECTOR_FIELD_GROUPS = (
    "Identity",
    "Geometry",
    "Materials",
    "Hardware",
    "Configuration",
    "Manufacturing",
    "Validation",
    "Metadata",
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
    manufacturing_runtime_pipeline_builder: Any | None = None
    manufacturing_production_package_builder: Any | None = None
    manufacturing_cost_pipeline_builder: Any | None = None
    manufacturing_commercial_pipeline_builder: Any | None = None


def _frame_layout(widget):
    layout = QtWidgets.QVBoxLayout(widget)
    if hasattr(layout, "setContentsMargins"):
        layout.setContentsMargins(8, 8, 8, 8)
    return layout


def _clear_layout(layout):
    if hasattr(layout, "items"):
        layout.items = []
    if hasattr(layout, "count") and hasattr(layout, "takeAt"):
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            widget = getattr(item, "widget", None)
            if callable(widget):
                child_widget = widget()
                if child_widget is not None and hasattr(child_widget, "setParent"):
                    child_widget.setParent(None)
                continue
            child_layout = getattr(item, "layout", None)
            if callable(child_layout):
                nested = child_layout()
                if nested is not None:
                    _clear_layout(nested)


def _inspector_field_group(name: str, label: str, explicit_group: str = "") -> str:
    explicit_group = (explicit_group or "").strip()
    if explicit_group:
        return explicit_group
    probe = f"{name} {label}".lower()
    if any(
        token in probe
        for token in (
            "selection_id",
            "display_name",
            "selection_type",
            "source_reference",
            "id",
            "name",
        )
    ):
        return "Identity"
    if any(
        token in probe
        for token in (
            "width",
            "height",
            "depth",
            "thickness",
            "diameter",
            "angle",
            "radius",
            "x",
            "y",
            "z",
            "geometry",
            "position",
            "size",
            "offset",
        )
    ):
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
            "Read-model driven preview placeholder backed by projection data.",
            parent=parent,
        )
        self.preview_modes: tuple[str, ...] = ConfiguratorV2ShellModel().preview_modes
        self.preview_mode_selector = QtWidgets.QComboBox()
        for mode in self.preview_modes:
            self.preview_mode_selector.addItem(mode)
        self.body_layout.addWidget(self.preview_mode_selector)
        self.read_model = empty_preview_read_model()
        self.preview_title_value = QtWidgets.QLabel("")
        self.preview_state_value = QtWidgets.QLabel("")
        self.current_object_value = QtWidgets.QLabel("")
        self.current_family_value = QtWidgets.QLabel("")
        self.preview_status_value = QtWidgets.QLabel("")
        self.representation_value = QtWidgets.QLabel("")
        self.highlight_target_value = QtWidgets.QLabel("")
        self.scene_available_value = QtWidgets.QLabel("")
        self.node_count_value = QtWidgets.QLabel("")
        self.scene_bounds_value = QtWidgets.QLabel("")
        self.selected_node_value = QtWidgets.QLabel("")
        self.representation_status_value = QtWidgets.QLabel("")
        self.warning_value = QtWidgets.QLabel("")
        self.viewport_message_value = QtWidgets.QLabel("")
        self.preview_placeholder = QtWidgets.QLabel("Preview unavailable")
        if hasattr(self.preview_placeholder, "setMinimumHeight"):
            self.preview_placeholder.setMinimumHeight(240)
        self.render_rows: list[str] = []
        self.summary_labels: dict[str, object] = {}
        self.highlighted_selection_id = ""
        self.highlighted_selection_type = "NONE"
        self.visual_components: tuple[VisualComponent, ...] = ()
        self.visual_styles: tuple[FurnitureVisualStyle, ...] = ()
        self.interactive_components: tuple[InteractiveVisualComponent, ...] = ()
        self._render_preview_state()

    def set_selection_highlight(self, selection: ConfiguratorSelection):
        self.highlighted_selection_id = selection.selection_id
        self.highlighted_selection_type = selection.selection_type
        self._render_preview_state()

    def _set_label_text(self, widget, value: str):
        if hasattr(widget, "setText"):
            widget.setText(value)

    def _append_summary(self, label_text: str, value_text: str):
        label_widget = QtWidgets.QLabel()
        self._set_label_text(label_widget, label_text)
        self.body_layout.addWidget(label_widget)
        value_widget = QtWidgets.QLabel()
        self._set_label_text(value_widget, value_text)
        self.body_layout.addWidget(value_widget)
        self.summary_labels[label_text] = value_widget
        self.render_rows.append(f"{label_text}: {value_text}")

    def _render_preview_state(self):
        _clear_layout(self.body_layout)
        self.summary_labels = {}
        self.render_rows = []

        read_model = self.read_model or empty_preview_read_model()
        if hasattr(self.preview_mode_selector, "setCurrentText"):
            self.preview_mode_selector.setCurrentText(read_model.preview_mode or "Customer View")
        self.body_layout.addWidget(self.preview_mode_selector)
        self._append_summary("Preview Title", read_model.preview_title or "Preview")
        self._append_summary("Preview Mode", read_model.preview_mode or "Customer View")
        self._append_summary("Preview State", read_model.preview_state or "Unavailable")
        self._append_summary("Scene Available", "Yes" if read_model.scene_available else "No")
        self._append_summary("Node Count", str(read_model.node_count))
        self._append_summary("Bounds", read_model.scene_bounds or "Unavailable")
        self._append_summary("Selected Node", read_model.selected_node or "None")
        self._append_summary(
            "Current Object",
            read_model.selected_node or read_model.highlighted_item_id or self.highlighted_selection_id or "None",
        )
        self._append_summary("Current Type", read_model.highlighted_item_type or self.highlighted_selection_type or "NONE")
        self._append_summary("Current Family", read_model.current_family or "Not selected")
        self._append_summary(
            "Representation Availability",
            ", ".join(read_model.available_representations) if read_model.available_representations else "Unavailable",
        )
        self._append_summary("Representation Status", read_model.representation_status or "Unavailable")
        self._append_summary(
            "Highlight Target",
            read_model.highlight_target or read_model.highlighted_item_id or self.highlighted_selection_id or "None",
        )
        self._append_summary("Warnings", ", ".join(read_model.warnings) if read_model.warnings else "None")
        self._append_summary(
            "Viewport Message",
            read_model.viewport_message or read_model.unsupported_reason or "Preview unavailable",
        )

        if self.visual_styles:
            self._append_summary("Visual Styles", f"{len(self.visual_styles)} style(s) active")
            for idx, style in enumerate(self.visual_styles):
                label_text = f"  Style {idx + 1}"
                summary = style_summary_label(style) or "Unnamed style"
                self._append_summary(label_text, summary)

        if self.interactive_components:
            counts = count_active_interactions(self.interactive_components)
            total = len(self.interactive_components)
            self._append_summary("Interactive Components", f"{total} active")
            selected_ic = next(
                (ic for ic in self.interactive_components if ic.interaction.overlay.selected),
                None,
            )
            highlighted_ic = next(
                (ic for ic in self.interactive_components if ic.interaction.overlay.highlighted),
                None,
            )
            if selected_ic:
                self._append_summary("  Selected", selected_ic.component_id or selected_ic.display_name)
            if highlighted_ic:
                self._append_summary("  Highlighted", highlighted_ic.component_id or highlighted_ic.display_name)

            hw_visible = any(ic.interaction.visibility.hardware_visible for ic in self.interactive_components)
            fm_visible = any(ic.interaction.visibility.feature_markers_visible for ic in self.interactive_components)
            ds_visible = any(ic.interaction.visibility.door_swing_visible for ic in self.interactive_components)
            do_visible = any(ic.interaction.visibility.drawer_open_visible for ic in self.interactive_components)

            self._append_summary("  Hardware Visible", "yes" if hw_visible else "no")
            self._append_summary("  Feature Markers Visible", "yes" if fm_visible else "no")
            self._append_summary("  Door Swing Indicators", "yes" if ds_visible else "no")
            self._append_summary("  Drawer Open Indicators", "yes" if do_visible else "no")

            state_summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
            if state_summary:
                self._append_summary("  State Counts", state_summary)

        # ── Presentation-aware display ───────────────────────────
        if self.interactive_components:
            synced_components = [
                ic for ic in self.interactive_components
                if ic.interaction.presentation is not None
                or ic.interaction.visual_contract is not None
            ]
            if synced_components:
                self._append_summary("Presentation Sync", f"{len(synced_components)} component(s) synced")
                for ic in synced_components[:5]:
                    label = f"  {ic.component_id or ic.display_name}"
                    parts = []
                    p = ic.interaction.presentation
                    vc = ic.interaction.visual_contract
                    if p is not None and not p.is_neutral:
                        parts.append(p.dominant_flag)
                        parts.append(f"sev={p.visual_severity}")
                    if vc is not None and not vc.is_neutral:
                        parts.append(vc.emphasis_level)
                        parts.append(vc.outline_intent)
                        if vc.opacity_intent != "NORMAL":
                            parts.append(vc.opacity_intent)
                    if parts:
                        self._append_summary(label, " | ".join(parts))
                    else:
                        self._append_summary(label, "neutral")

        placeholder_text = read_model.viewport_message or read_model.unsupported_reason or "Preview unavailable"
        if read_model.available_representations:
            placeholder_text = f"{placeholder_text} | Representations: {', '.join(read_model.available_representations)}"
        self.preview_placeholder = QtWidgets.QLabel()
        self._set_label_text(self.preview_placeholder, placeholder_text)
        if hasattr(self.preview_placeholder, "setMinimumHeight"):
            self.preview_placeholder.setMinimumHeight(240)
        self.body_layout.addWidget(self.preview_placeholder)

    def set_read_model(self, read_model: PreviewReadModel):
        self.read_model = read_model or empty_preview_read_model()
        self.highlighted_selection_id = (
            self.read_model.selected_node
            or self.read_model.highlight_target
            or self.read_model.highlighted_item_id
            or self.highlighted_selection_id
        )
        self.highlighted_selection_type = self.read_model.highlighted_item_type or self.highlighted_selection_type
        self._render_preview_state()

    def set_visual_components(
        self,
        components: tuple[VisualComponent, ...],
        *,
        read_model: PreviewReadModel | None = None,
    ):
        self.visual_components = tuple(components or ())
        self.visual_styles = apply_furniture_visual_styles(self.visual_components)
        self.set_read_model(
            read_model
            or build_preview_read_model(
                {
                    "visual_components": self.visual_components,
                }
            )
        )

    def set_interactive_components(
        self,
        interactive: tuple[InteractiveVisualComponent, ...],
        read_model: PreviewReadModel | None = None,
    ):
        self.interactive_components = tuple(interactive or ())
        self.visual_components = ()
        self.visual_styles = ()
        self.set_read_model(
            read_model
            or build_preview_read_model(
                {
                    "interactive_components": self.interactive_components,
                }
            )
        )


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
    SUMMARY_ALIASES = {
        "Selection Type": "selection_type_value",
        "Display Name": "display_name_value",
        "Selection ID": "selection_id_value",
        "Source Reference": "source_region_value",
        "Warnings": "metadata_value",
    }

    def __init__(self, parent=None, on_field_commit=None):
        super().__init__(
            "Inspector",
            "Selected object read model and grouped metadata.",
            parent=parent,
        )
        self.on_field_commit = on_field_commit
        self.read_model = empty_inspector_read_model()
        self.render_rows: list[str] = []
        self.selection_summary_values: dict[str, object] = {}
        self.field_group_rows: dict[str, list[object]] = {group: [] for group in INSPECTOR_FIELD_GROUPS}
        self.group_headers: dict[str, object] = {}
        self.group_containers: dict[str, object] = {}
        self.group_field_labels: dict[str, list[object]] = {group: [] for group in INSPECTOR_FIELD_GROUPS}
        self.editable_field_inputs: dict[str, object] = {}

        self._rebuild_render_state()

    def _append_summary_row(self, label_text: str, value_text: str):
        label_widget = QtWidgets.QLabel(label_text)
        if hasattr(label_widget, "setText"):
            label_widget.setText(label_text)
        self.body_layout.addWidget(label_widget)
        value_widget = QtWidgets.QLabel()
        if hasattr(value_widget, "setText"):
            value_widget.setText(value_text)
        self.body_layout.addWidget(value_widget)
        self.selection_summary_values[label_text] = value_widget
        alias_name = self.SUMMARY_ALIASES.get(label_text)
        if alias_name:
            setattr(self, alias_name, value_widget)
        self.render_rows.append(f"{label_text}: {value_text}")

    def _append_field_group(self, group_name: str, fields):
        header = QtWidgets.QLabel()
        if hasattr(header, "setText"):
            header.setText(group_name)
        self.body_layout.addWidget(header)
        self.group_headers[group_name] = header
        self.render_rows.append(group_name)
        group_rows = []
        for field in fields:
            value_text = field.value if not field.unit else f"{field.value} {field.unit}".strip()
            row_text = f"{field.label}: {value_text}"
            if field.source_reference:
                row_text = f"{row_text} [{field.source_reference}]"
            label = QtWidgets.QLabel()
            if hasattr(label, "setText"):
                label.setText(row_text)
            self.body_layout.addWidget(label)
            group_rows.append(label)
            self.group_field_labels.setdefault(group_name, []).append(label)
            self.render_rows.append(f"{group_name} | {row_text}")
            if field.editable and field.name in {"width_mm", "height_mm", "depth_mm", "shelf_count", "door_count"}:
                editor_cls = getattr(QtWidgets, "QLineEdit", None)
                if editor_cls is not None:
                    editor = editor_cls()
                    if hasattr(editor, "setText"):
                        editor.setText(field.value)
                    if hasattr(editor, "editingFinished") and callable(self.on_field_commit):
                        editor.editingFinished.connect(
                            lambda field_name=field.name, line_edit=editor: self.commit_field_edit(
                                field_name,
                                line_edit.text() if hasattr(line_edit, "text") else "",
                            )
                        )
                    self.body_layout.addWidget(editor)
                    self.editable_field_inputs[field.name] = editor
        self.field_group_rows[group_name] = group_rows

    def _rebuild_render_state(self):
        _clear_layout(self.body_layout)
        self.render_rows = []
        self.selection_summary_values = {}
        self.field_group_rows = {group: [] for group in INSPECTOR_FIELD_GROUPS}
        self.group_headers = {}
        self.group_containers = {}
        self.group_field_labels = {group: [] for group in INSPECTOR_FIELD_GROUPS}
        self.editable_field_inputs = {}

        read_model = self.read_model or empty_inspector_read_model()
        warnings_text = ", ".join(read_model.warnings) if read_model.warnings else "None"
        self._append_summary_row("Selection Type", read_model.selection_type or "NONE")
        self._append_summary_row("Display Name", read_model.display_name or "Not selected")
        self._append_summary_row("Selection ID", read_model.selection_id or "")
        self._append_summary_row("Source Reference", read_model.source_reference or "")
        self._append_summary_row("Stale Status", "STALE" if read_model.stale else "Fresh")
        self._append_summary_row("Unsupported Status", "Unsupported" if read_model.unsupported else "Supported")
        self._append_summary_row("Unsupported Reason", read_model.unsupported_reason or "None")
        self._append_summary_row("Suggested Action", read_model.suggested_action or "None")
        self._append_summary_row("Warnings", warnings_text)

        grouped_fields: dict[str, list[object]] = {group: [] for group in INSPECTOR_FIELD_GROUPS}
        for field in read_model.fields:
            group_name = _inspector_field_group(field.name, field.label, field.group)
            grouped_fields.setdefault(group_name, []).append(field)

        for group_name in INSPECTOR_FIELD_GROUPS:
            self._append_field_group(group_name, grouped_fields.get(group_name, ()))

        for group_name, fields in grouped_fields.items():
            if group_name not in INSPECTOR_FIELD_GROUPS and fields:
                self._append_field_group(group_name, fields)

    def set_read_model(self, read_model: InspectorReadModel):
        self.read_model = read_model or empty_inspector_read_model()
        self._rebuild_render_state()

    def set_selection(self, selection: ConfiguratorSelection):
        self.set_read_model(build_inspector_read_model(selection))

    def commit_field_edit(self, field_name: str, value: str):
        if not callable(self.on_field_commit):
            return
        self.on_field_commit(field_name, value)


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
        self.active_engineering_state = ActiveEngineeringState()
        self.project_tree_read_model = empty_project_tree_read_model()
        self.inspector_read_model = empty_inspector_read_model()
        self.preview_read_model = empty_preview_read_model()
        self.preview_visual_components: tuple[VisualComponent, ...] = ()
        self.message_center_read_model = empty_message_center_read_model()
        self.review_panel_read_models = empty_review_panel_read_models(
            self.review_panel_names
        )
        self.foi_presentation_read_model: ReviewPanelReadModel = ReviewPanelReadModel(
            panel_name="Factory Operations",
        )
        self._foi_readiness: Any = None
        self._foi_blocking: Any = None
        self._foi_recommendations: Any = None
        self._foi_decision: Any = None
        self._nesting_savings_report: Any = None
        self._nesting_savings_dashboard_section: Any = None
        self._manufacturing_production_package: Any = None
        self._manufacturing_cost_summary: Any = None
        self._manufacturing_commercial_result: Any = None
        self.factory_dashboard_read_model: FactoryDashboardReadModel | None = None

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
        self.inspector_region = InspectorRegion(on_field_commit=self._handle_inspector_field_commit)
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
        source = selection
        # Enrich with ActiveEngineeringState specification if available
        active_state = getattr(self, "active_engineering_state", None)
        if active_state is not None and getattr(active_state, "specification", None) is not None:
            source = enrich_inspector_source_with_specification(source, active_state)
        self.set_inspector_read_model(build_inspector_read_model(source))
        self.set_preview_read_model(
            build_preview_read_model(
                {
                    "selection": selection,
                    "current_family": self.current_product_family,
                    "preview_title": self.current_product_family or selection.display_name or "Preview",
                    "preview_state": "Ready" if selection.selection_type not in ("", "NONE") else "Unavailable",
                    "viewport_message": (
                        f"Focus on {selection.display_name or selection.selection_id or 'current selection'}"
                        if selection.selection_type not in ("", "NONE")
                        else "Select a project or product to populate preview"
                    ),
                    "available_representations": (
                        ("Customer View", "Design View")
                        if selection.selection_type not in ("", "NONE")
                        else ()
                    ),
                    "highlight_representation": "Selection Focus"
                    if selection.selection_type not in ("", "NONE")
                    else "",
                    "warnings": (),
                }
            )
        )
        self.preview_region.set_selection_highlight(selection)

    def clear_selection(self):
        self.set_selection(ConfiguratorSelection())

    def attach_service_integration(self, service_integration):
        self.service_integration = service_integration

    def _handle_inspector_field_commit(self, field_name: str, value: str):
        if self.service_integration is None:
            return
        try:
            if field_name in ("shelf_count", "door_count"):
                parsed_value = int(value)
            else:
                parsed_value = float(value)
        except (TypeError, ValueError):
            return
        if field_name == "width_mm":
            self.service_integration.update_active_base_cabinet_width(parsed_value)
        elif field_name == "height_mm":
            self.service_integration.update_active_base_cabinet_height(parsed_value)
        elif field_name == "depth_mm":
            self.service_integration.update_active_base_cabinet_depth(parsed_value)
        elif field_name == "shelf_count":
            self.service_integration.update_active_base_cabinet_shelf_count(parsed_value)
        elif field_name == "door_count":
            self.service_integration.update_active_base_cabinet_door_count(parsed_value)

    def set_project_tree_read_model(self, read_model: ProjectTreeReadModel):
        self.project_tree_read_model = read_model
        self.project_tree_region.set_read_model(read_model)

    def set_inspector_read_model(self, read_model: InspectorReadModel):
        self.inspector_read_model = read_model
        self.inspector_region.set_read_model(read_model)

    def set_preview_read_model(self, read_model: PreviewReadModel):
        self.preview_visual_components = ()
        self.preview_read_model = read_model
        self.preview_region.set_read_model(read_model)

    def set_preview_visual_components(
        self,
        components: tuple[VisualComponent, ...],
        read_model: PreviewReadModel | None = None,
    ):
        self.preview_visual_components = tuple(components or ())
        if read_model is None:
            read_model = build_preview_read_model({"visual_components": self.preview_visual_components})
        self.preview_read_model = read_model
        self.preview_region.set_visual_components(self.preview_visual_components, read_model=read_model)

    def set_preview_interactive_components(
        self,
        interactive: tuple[InteractiveVisualComponent, ...],
        read_model: PreviewReadModel | None = None,
    ):
        self.preview_visual_components = ()
        if read_model is None:
            read_model = build_preview_read_model({"interactive_components": interactive})
        self.preview_read_model = read_model
        self.preview_region.set_interactive_components(interactive, read_model=read_model)

    def synchronize_preview_interactive_components(
        self,
        interactive: tuple[InteractiveVisualComponent, ...],
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
    ):
        """Synchronize presentation state onto interactive components and update preview.

        Runs the full presentation pipeline (binding → visual contract) on the
        interactive component IDs, attaches the results to new frozen instances,
        and routes them into the preview region.

        The original *interactive* tuple is unchanged.
        """
        synchronized = _attach_synchronized_states(
            interactive,
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
        self.set_preview_interactive_components(synchronized)

    def set_message_center_read_model(self, read_model: MessageCenterReadModel):
        self.message_center_read_model = read_model

    def set_presentation_aware_inspector(
        self,
        selection: ConfiguratorSelection | None,
        interactive_component: InteractiveVisualComponent | None = None,
    ):
        """Update inspector with optional presentation-aware fields.

        Builds the base inspector read model from *selection*, then
        appends presentation state and visual contract fields when
        *interactive_component* is provided and carries presentation data.

        The base inspector behavior is unchanged when interactive_component
        is None or has no presentation data.
        """
        selection = selection or ConfiguratorSelection()
        base_model = build_inspector_read_model(selection)

        if interactive_component is not None and interactive_component.interaction.presentation is not None:
            extra_fields = _build_presentation_inspector_fields(interactive_component)
            merged_fields = base_model.fields + extra_fields
            merged_model = InspectorReadModel(
                selection_id=base_model.selection_id,
                selection_type=base_model.selection_type,
                display_name=base_model.display_name,
                fields=merged_fields,
                warnings=base_model.warnings,
                source_reference=base_model.source_reference,
                unsupported=base_model.unsupported,
                unsupported_reason=base_model.unsupported_reason,
                suggested_action=base_model.suggested_action,
                stale=base_model.stale,
            )
            self.set_inspector_read_model(merged_model)
        else:
            self.set_inspector_read_model(base_model)

    def set_review_panel_read_models(
        self,
        read_models: tuple[ReviewPanelReadModel, ...],
    ):
        self.review_panel_read_models = tuple(read_models or ())

    def set_foi_presentation_read_model(
        self,
        read_model: ReviewPanelReadModel | None = None,
    ):
        self.foi_presentation_read_model = read_model or ReviewPanelReadModel(
            panel_name="Factory Operations",
        )

    def set_foi_read_models(
        self,
        *,
        readiness: Any = None,
        blocking: Any = None,
        recommendations: Any = None,
        decision: Any = None,
    ):
        """Store FOI intermediate read models so refresh_dashboard can reuse them."""
        self._foi_readiness = readiness
        self._foi_blocking = blocking
        self._foi_recommendations = recommendations
        self._foi_decision = decision

    def set_factory_dashboard_read_model(
        self,
        read_model: FactoryDashboardReadModel | None = None,
    ):
        from factory_dashboard import FactoryDashboardReadModel as _DashModel
        self.factory_dashboard_read_model = read_model or _DashModel()

    def set_nesting_savings_report(
        self,
        savings_report: Any = None,
    ):
        self._nesting_savings_report = savings_report

    def set_nesting_savings_dashboard_section(
        self,
        section: Any = None,
    ):
        self._nesting_savings_dashboard_section = section

    def set_manufacturing_result(self, production_package: Any = None):
        self._manufacturing_production_package = production_package

    def set_cost_result(self, cost_summary: Any = None):
        self._manufacturing_cost_summary = cost_summary

    def set_commercial_result(self, commercial_result: Any = None):
        self._manufacturing_commercial_result = commercial_result


def create_configurator_v2_workspace(
    parent=None,
    *,
    service_bindings: ConfiguratorV2ServiceBindings | None = None,
) -> ConfiguratorV2Workspace:
    return ConfiguratorV2Workspace(parent=parent, service_bindings=service_bindings)


# ── Presentation integration helper ─────────────────────────────────


def _attach_synchronized_states(
    interactives: tuple[InteractiveVisualComponent, ...],
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
) -> tuple[InteractiveVisualComponent, ...]:
    """Synchronize presentation state + visual contract onto interactive components.

    Accepts a sequence of InteractiveVisualComponent instances and
    presentation flag ID sets, runs the full synchronization pipeline,
    and returns NEW InteractiveVisualComponent instances with the
    ``presentation`` and ``visual_contract`` fields populated.

    The original sequence is unchanged (frozen dataclasses).

    This is a deterministic, side-effect free operation.
    """
    if not interactives:
        return ()

    ids = tuple(ic.component_id for ic in interactives)
    snapshots = synchronize_presentation(
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

    result: list[InteractiveVisualComponent] = []
    for ic, snap in zip(interactives, snapshots):
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
                    presentation=(
                        snap.presentation_state
                        if not snap.presentation_state.is_neutral
                        else None
                    ),
                    visual_contract=(
                        snap.visual_contract
                        if not snap.visual_contract.is_neutral
                        else None
                    ),
                ),
            )
        )
    return tuple(result)


# ── Presentation inspector helper ────────────────────────────────────


def _build_presentation_inspector_fields(
    interactive: InteractiveVisualComponent,
) -> tuple[InspectorFieldReadModel, ...]:
    """Build inspector field entries from an interactive component's presentation state.

    Returns InspectorFieldReadModel entries for ``Presentation`` group
    when the component carries presentation or visual contract data.

    Returns empty tuple when the component has no presentation data.
    """
    if interactive is None:
        return ()

    interaction = interactive.interaction
    presentation = interaction.presentation
    contract = interaction.visual_contract

    if presentation is None and contract is None:
        return ()

    fields: list[InspectorFieldReadModel] = []

    # ── Identity
    fields.append(
        InspectorFieldReadModel(
            name="presentation_component_id",
            label="Presentation Component ID",
            value=interactive.component_id,
            group="Presentation",
        )
    )
    fields.append(
        InspectorFieldReadModel(
            name="presentation_state",
            label="Presentation State",
            value=interaction.state_label,
            group="Presentation",
        )
    )

    # ── Presentation state flags
    if presentation is not None and not presentation.is_neutral:
        fields.append(
            InspectorFieldReadModel(
                name="presentation_flags",
                label="Active Flags",
                value=", ".join(presentation.active_flags) if presentation.active_flags else "none",
                group="Presentation",
            )
        )
        fields.append(
            InspectorFieldReadModel(
                name="presentation_dominant",
                label="Dominant Flag",
                value=presentation.dominant_flag,
                group="Presentation",
            )
        )
        fields.append(
            InspectorFieldReadModel(
                name="presentation_severity",
                label="Visual Severity",
                value=str(presentation.visual_severity),
                group="Presentation",
            )
        )

    # ── Visual contract tokens
    if contract is not None and not contract.is_neutral:
        fields.append(
            InspectorFieldReadModel(
                name="vc_emphasis",
                label="Emphasis Level",
                value=contract.emphasis_level,
                group="Presentation",
            )
        )
        fields.append(
            InspectorFieldReadModel(
                name="vc_outline",
                label="Outline Intent",
                value=contract.outline_intent,
                group="Presentation",
            )
        )
        fields.append(
            InspectorFieldReadModel(
                name="vc_opacity",
                label="Opacity Intent",
                value=contract.opacity_intent,
                group="Presentation",
            )
        )
        fields.append(
            InspectorFieldReadModel(
                name="vc_priority",
                label="Interaction Priority",
                value=str(contract.interaction_priority),
                group="Presentation",
            )
        )

    return tuple(fields)
