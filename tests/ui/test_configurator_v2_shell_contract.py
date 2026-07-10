import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


class _FakeSignal:
    def connect(self, _callback):
        return None


class _FakeWidget:
    def __init__(self, *args, **kwargs):
        self._layout = None
        self._object_name = ""
        self._enabled = True
        self._text = ""
        self._minimum_width = None
        self._maximum_width = None
        self.children = []

    def setLayout(self, layout):
        self._layout = layout

    def layout(self):
        return self._layout

    def setObjectName(self, name):
        self._object_name = name

    def objectName(self):
        return self._object_name

    def setEnabled(self, enabled):
        self._enabled = bool(enabled)

    def setMinimumHeight(self, _height):
        return None

    def setWordWrap(self, _enabled):
        return None

    def setReadOnly(self, _enabled):
        return None

    def setMaximumHeight(self, _height):
        return None

    def setMinimumWidth(self, width):
        self._minimum_width = width

    def setMaximumWidth(self, width):
        self._maximum_width = width

    def setPlaceholderText(self, _text):
        return None

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text


class _FakeMainWindow(_FakeWidget):
    def setCentralWidget(self, widget):
        self.children.append(widget)


class _FakeTextEdit(_FakeWidget):
    def hide(self):
        return None

    def show(self):
        return None


class _FakeLayout:
    def __init__(self, *args, **kwargs):
        self.items = []
        if args:
            parent = args[0]
            if hasattr(parent, "setLayout") and callable(parent.setLayout):
                parent.setLayout(self)

    def addWidget(self, widget):
        self.items.append(widget)

    def addLayout(self, layout):
        self.items.append(layout)

    def addRow(self, *_args):
        self.items.append(_args)


class _FakeComboBox(_FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []
        self.currentIndexChanged = _FakeSignal()

    def addItem(self, text):
        self.items.append(text)


class _FakeButton(_FakeWidget):
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text
        self.clicked = _FakeSignal()


class _FakeLabel(_FakeWidget):
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text


class _FakeTabWidget(_FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tabs = []
        self._current_index = 0
        self._current_widget = None

    def addTab(self, widget, title):
        self.tabs.append((widget, title))
        if self._current_widget is None:
            self._current_widget = widget

    def setCurrentIndex(self, index):
        self._current_index = index
        if 0 <= index < len(self.tabs):
            self._current_widget = self.tabs[index][0]

    def currentIndex(self):
        return self._current_index

    def setCurrentWidget(self, widget):
        self._current_widget = widget
        for index, (candidate, _title) in enumerate(self.tabs):
            if candidate is widget:
                self._current_index = index
                break

    def currentWidget(self):
        return self._current_widget


class _FakeScrollArea(_FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._widget_resizable = False
        self._widget = None

    def setWidgetResizable(self, resizable):
        self._widget_resizable = bool(resizable)

    def widgetResizable(self):
        return self._widget_resizable

    def setWidget(self, widget):
        self._widget = widget

    def widget(self):
        return self._widget


class _FakeSplitter(_FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets = []
        self._orientation = None
        self._children_collapsible = None
        self._sizes = []

    def setOrientation(self, orientation):
        self._orientation = orientation

    def setChildrenCollapsible(self, collapsible):
        self._children_collapsible = bool(collapsible)

    def addWidget(self, widget):
        self.widgets.append(widget)

    def setStretchFactor(self, *_args):
        return None

    def setSizes(self, sizes):
        self._sizes = list(sizes)


def _fake_qt_module():
    fake_qt_widgets = types.SimpleNamespace(
        QMainWindow=_FakeMainWindow,
        QWidget=_FakeWidget,
        QFrame=_FakeWidget,
        QVBoxLayout=_FakeLayout,
        QHBoxLayout=_FakeLayout,
        QFormLayout=_FakeLayout,
        QComboBox=_FakeComboBox,
        QPushButton=_FakeButton,
        QLabel=_FakeLabel,
        QTabWidget=_FakeTabWidget,
        QCheckBox=_FakeWidget,
        QDoubleSpinBox=_FakeWidget,
        QSpinBox=_FakeWidget,
        QTextEdit=_FakeTextEdit,
        QGroupBox=_FakeWidget,
        QScrollArea=_FakeScrollArea,
        QSplitter=_FakeSplitter,
        QFileDialog=types.SimpleNamespace(getSaveFileName=lambda *args, **kwargs: ("", "")),
        QMessageBox=types.SimpleNamespace(information=lambda *args, **kwargs: None),
    )
    class _FakeTimer(_FakeWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.timeout = _FakeSignal()

        def setSingleShot(self, _enabled):
            return None

    fake_qt_core = types.SimpleNamespace(QTimer=_FakeTimer)
    return types.SimpleNamespace(QtWidgets=fake_qt_widgets, QtCore=fake_qt_core)


def _fake_runtime_modules():
    fake_freecad_gui = types.ModuleType("FreeCADGui")
    fake_freecad_gui.listCommands = lambda: []
    fake_freecad_gui.addCommand = lambda *args, **kwargs: None
    fake_freecad_gui.addWorkbench = lambda *args, **kwargs: None
    fake_freecad = types.ModuleType("FreeCAD")
    fake_part = types.ModuleType("Part")
    return {
        "FreeCADGui": fake_freecad_gui,
        "FreeCAD": fake_freecad,
        "Part": fake_part,
    }


class TestConfiguratorV2ShellContract(unittest.TestCase):
    def _import_workspace_module(self):
        with patch.dict(
            sys.modules,
            {"core.qt_compat": _fake_qt_module()},
        ):
            sys.modules.pop("ui.configurator_v2.workspace", None)
            return importlib.import_module("ui.configurator_v2.workspace")

    def test_shell_can_be_imported_and_constructed(self):
        module = self._import_workspace_module()

        workspace = module.create_configurator_v2_workspace()

        self.assertEqual(workspace.workspace_areas, module.WORKSPACE_AREAS)
        self.assertEqual(workspace.navigation_entries, module.NAVIGATION_ENTRIES)
        self.assertEqual(workspace.project_tree_nodes, module.PROJECT_TREE_NODES)
        self.assertEqual(workspace.product_states, module.PRODUCT_STATES)
        self.assertEqual(workspace.action_names, module.ACTION_NAMES)
        self.assertEqual(workspace.preview_modes, module.PREVIEW_MODES)
        self.assertEqual(workspace.review_panel_names, module.REVIEW_PANEL_NAMES)
        self.assertEqual(workspace.message_categories, module.MESSAGE_CATEGORIES)
        self.assertTrue(hasattr(workspace, "global_navigation_region"))
        self.assertTrue(hasattr(workspace, "project_tree_region"))
        self.assertTrue(hasattr(workspace, "preview_region"))
        self.assertTrue(hasattr(workspace, "project_context_region"))
        self.assertTrue(hasattr(workspace, "product_state_indicator"))
        self.assertTrue(hasattr(workspace, "inspector_region"))
        self.assertTrue(hasattr(workspace, "review_region"))
        self.assertTrue(hasattr(workspace, "message_center_region"))
        self.assertTrue(hasattr(workspace, "action_bar_region"))

    def test_action_names_exist_and_buttons_are_wired(self):
        module = self._import_workspace_module()
        workspace = module.create_configurator_v2_workspace()

        self.assertEqual(
            tuple(workspace.action_bar_region.action_buttons.keys()),
            module.ACTION_NAMES,
        )
        self.assertEqual(
            tuple(workspace.action_bar_region.action_handlers.keys()),
            module.ACTION_NAMES,
        )
        self.assertTrue(
            all(
                getattr(button, "_enabled", False)
                for button in workspace.action_bar_region.action_buttons.values()
            )
        )

    def test_workspace_regions_and_state_metadata_exist(self):
        module = self._import_workspace_module()
        workspace = module.create_configurator_v2_workspace()

        self.assertEqual(
            tuple(workspace.global_navigation_region.navigation_entries.keys()),
            module.NAVIGATION_ENTRIES,
        )
        self.assertEqual(
            tuple(workspace.product_state_indicator.states),
            module.PRODUCT_STATES,
        )
        self.assertEqual(
            tuple(workspace.review_region.review_containers.keys()),
            module.REVIEW_PANEL_NAMES,
        )
        self.assertEqual(
            workspace.project_context_region.current_product_state,
            "Draft",
        )

    def test_root_workspace_uses_scroll_area_and_keeps_footer_regions(self):
        module = self._import_workspace_module()
        workspace = module.create_configurator_v2_workspace()

        self.assertIsNotNone(workspace.root_scroll_area)
        self.assertTrue(workspace.root_scroll_area.widgetResizable())
        self.assertIs(workspace.root_scroll_area.widget(), workspace.root_scroll_content)
        self.assertIsNotNone(workspace.root_scroll_content_layout)
        self.assertIn(workspace.header_region, workspace.root_scroll_content_layout.items)
        self.assertIn(workspace.workspace_splitter, workspace.root_scroll_content_layout.items)
        self.assertIn(workspace.bottom_tabs, workspace.root_scroll_content_layout.items)
        self.assertIn(workspace.action_bar_region, workspace.root_scroll_content_layout.items)
        self.assertLess(
            workspace.root_scroll_content_layout.items.index(workspace.header_region),
            workspace.root_scroll_content_layout.items.index(workspace.workspace_splitter),
        )
        self.assertLess(
            workspace.root_scroll_content_layout.items.index(workspace.workspace_splitter),
            workspace.root_scroll_content_layout.items.index(workspace.bottom_tabs),
        )
        self.assertLess(
            workspace.root_scroll_content_layout.items.index(workspace.bottom_tabs),
            workspace.root_scroll_content_layout.items.index(workspace.action_bar_region),
        )

    def test_header_region_contains_context_and_state_widgets(self):
        module = self._import_workspace_module()
        workspace = module.create_configurator_v2_workspace()

        self.assertIsNotNone(workspace.header_region)
        self.assertIn(workspace.project_context_region, workspace.header_region.layout().items)
        self.assertIn(workspace.product_state_indicator, workspace.header_region.layout().items)

    def test_splitter_layout_biases_preview_and_keeps_panes_ordered(self):
        module = self._import_workspace_module()
        workspace = module.create_configurator_v2_workspace()

        self.assertTrue(hasattr(workspace, "workspace_splitter"))
        self.assertEqual(len(workspace.workspace_splitter.widgets), 3)
        self.assertIs(workspace.workspace_splitter.widgets[0], workspace.left_pane)
        self.assertIs(workspace.workspace_splitter.widgets[1], workspace.center_pane)
        self.assertIs(workspace.workspace_splitter.widgets[2], workspace.right_pane)
        self.assertEqual(workspace.workspace_splitter._sizes, [160, 960, 280])
        self.assertEqual(workspace.left_pane._maximum_width, 220)
        self.assertEqual(workspace.center_pane._minimum_width, 760)
        self.assertEqual(workspace.right_pane._minimum_width, 280)
        self.assertIn(workspace.preview_region, workspace.center_pane.layout().items)
        self.assertIn(workspace.inspector_region, workspace.right_pane.layout().items)
        self.assertNotIn(workspace.project_context_region, workspace.right_pane.layout().items)
        self.assertNotIn(workspace.product_state_indicator, workspace.right_pane.layout().items)
        self.assertNotIn(workspace.review_region, workspace.right_pane.layout().items)

    def test_bottom_tabs_host_review_and_message_center(self):
        module = self._import_workspace_module()
        workspace = module.create_configurator_v2_workspace()

        self.assertIsNotNone(workspace.bottom_tabs)
        self.assertEqual(
            workspace.bottom_tabs.tabs,
            [
                (workspace.review_region, "Review"),
                (workspace.message_center_region, "Messages"),
            ],
        )

    def test_selection_model_updates_ui_state_only(self):
        module = self._import_workspace_module()
        workspace = module.create_configurator_v2_workspace(
            service_bindings=module.ConfiguratorV2ServiceBindings(
                project_application_service=Mock(),
                engineering_application_service=Mock(),
                manufacturing_application_service=Mock(),
            )
        )

        self.assertEqual(workspace.current_selection.selection_type, "NONE")

        selection = module.ConfiguratorSelection(
            selection_type="DOOR",
            selection_id="door-01",
            display_name="Left Door",
            source_region="ProjectTreeRegion",
            metadata={"role": "front"},
        )
        workspace.set_selection(selection)

        self.assertIs(workspace.current_selection, selection)
        self.assertEqual(
            workspace.inspector_region.selection_type_value.text(),
            "DOOR",
        )
        self.assertEqual(
            workspace.inspector_region.display_name_value.text(),
            "Left Door",
        )
        self.assertEqual(
            workspace.inspector_region.selection_id_value.text(),
            "door-01",
        )
        self.assertEqual(
            workspace.preview_region.highlighted_selection_id,
            "door-01",
        )
        self.assertEqual(
            workspace.preview_region.highlighted_selection_type,
            "DOOR",
        )
        workspace.clear_selection()
        self.assertEqual(workspace.current_selection.selection_type, "NONE")
        self.assertEqual(workspace.inspector_region.selection_type_value.text(), "NONE")
        self.assertEqual(workspace.preview_region.highlighted_selection_type, "NONE")

        workspace.service_bindings.project_application_service.execute.assert_not_called()
        workspace.service_bindings.engineering_application_service.execute.assert_not_called()
        workspace.service_bindings.manufacturing_application_service.execute.assert_not_called()

    def test_project_tree_select_node_routes_to_workspace_selection(self):
        module = self._import_workspace_module()
        workspace = module.create_configurator_v2_workspace()

        workspace.project_tree_region.select_node("Project")

        self.assertEqual(workspace.project_tree_region.selected_node, "Project")
        self.assertEqual(workspace.current_selection.selection_type, "PROJECT")
        self.assertEqual(workspace.current_selection.selection_id, "Project")
        self.assertEqual(
            workspace.inspector_region.display_name_value.text(),
            "Project",
        )

    def test_shell_construction_does_not_import_backend_services(self):
        module = self._import_workspace_module()

        backend_modules = (
            "application.project_application_service",
            "application.engineering_application_service",
            "application.manufacturing_application_service",
            "domain.base_cabinet_product_workflow",
            "manufacturing.manufacturing_commercial_pipeline_builder",
            "cost_intelligence.manufacturing_commercial_pipeline_builder",
        )

        for backend_module in backend_modules:
            sys.modules.pop(backend_module, None)

        module.create_configurator_v2_workspace()

        for backend_module in backend_modules:
            self.assertNotIn(backend_module, sys.modules)

    def test_service_bindings_are_injection_points_only(self):
        module = self._import_workspace_module()
        bindings = module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )

        workspace = module.create_configurator_v2_workspace(
            service_bindings=bindings,
        )

        self.assertIs(workspace.service_bindings, bindings)
        bindings.project_application_service.execute.assert_not_called()
        bindings.engineering_application_service.execute.assert_not_called()
        bindings.manufacturing_application_service.execute.assert_not_called()

    def test_legacy_configurator_still_imports(self):
        with patch.dict(
            sys.modules,
            _fake_runtime_modules() | {"core.qt_compat": _fake_qt_module()},
        ):
            legacy_module = importlib.import_module("ui.main_window")

        self.assertTrue(hasattr(legacy_module, "UIManager"))


if __name__ == "__main__":
    unittest.main()
