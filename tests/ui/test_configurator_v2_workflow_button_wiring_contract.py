import importlib
import sys
import types
import unittest
from unittest.mock import patch


class _FakeSignal:
    def __init__(self):
        self._callbacks = []

    def connect(self, callback):
        self._callbacks.append(callback)

    def emit(self, *args, **kwargs):
        for callback in tuple(self._callbacks):
            callback(*args, **kwargs)


class _FakeWidget:
    def __init__(self, *args, **kwargs):
        self._layout = None
        self._enabled = True
        self._text = ""

    def setLayout(self, layout):
        self._layout = layout

    def layout(self):
        return self._layout

    def setEnabled(self, enabled):
        self._enabled = bool(enabled)

    def setMinimumHeight(self, _height):
        return None

    def setMaximumHeight(self, _height):
        return None

    def setMinimumWidth(self, _width):
        return None

    def setMaximumWidth(self, _width):
        return None

    def setWordWrap(self, _enabled):
        return None

    def setCheckable(self, _enabled):
        return None

    def setChecked(self, _enabled):
        return None

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text


class _FakeLayout:
    def __init__(self, *args, **kwargs):
        self.items = []
        if args:
            parent = args[0]
            if hasattr(parent, "setLayout"):
                parent.setLayout(self)

    def addWidget(self, widget):
        self.items.append(widget)

    def addLayout(self, layout):
        self.items.append(layout)

    def addRow(self, *_args):
        self.items.append(_args)

    def setContentsMargins(self, *_args):
        return None

    def setSpacing(self, *_args):
        return None


class _FakeButton(_FakeWidget):
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text
        self.clicked = _FakeSignal()

    def click(self):
        self.clicked.emit(False)


class _FakeLabel(_FakeWidget):
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text


class _FakeComboBox(_FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []
        self.currentIndexChanged = _FakeSignal()

    def addItem(self, text):
        self.items.append(text)


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
    def setWidgetResizable(self, _resizable):
        return None

    def setWidget(self, _widget):
        return None


class _FakeSplitter(_FakeWidget):
    def addWidget(self, _widget):
        return None

    def setOrientation(self, _orientation):
        return None

    def setChildrenCollapsible(self, _collapsible):
        return None

    def setStretchFactor(self, *_args):
        return None

    def setSizes(self, _sizes):
        return None


def _fake_qt_module():
    class _FakeTimer:
        @staticmethod
        def singleShot(_ms, callback):
            callback()

    return types.SimpleNamespace(
        QtWidgets=types.SimpleNamespace(
            QWidget=_FakeWidget,
            QFrame=_FakeWidget,
            QVBoxLayout=_FakeLayout,
            QHBoxLayout=_FakeLayout,
            QFormLayout=_FakeLayout,
            QComboBox=_FakeComboBox,
            QPushButton=_FakeButton,
            QLabel=_FakeLabel,
            QTabWidget=_FakeTabWidget,
            QScrollArea=_FakeScrollArea,
            QSplitter=_FakeSplitter,
        ),
        QtCore=types.SimpleNamespace(
            QTimer=_FakeTimer,
            Qt=types.SimpleNamespace(Horizontal=1),
        ),
    )


class TestConfiguratorV2WorkflowButtonWiringContract(unittest.TestCase):
    def _import_modules(self):
        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt_module()}):
            workspace_module = importlib.import_module("ui.configurator_v2.workspace")
            integration_module = importlib.import_module("ui.configurator_v2.service_integration")
            engineering_state_module = importlib.import_module("ui.configurator_v2.engineering_state")
        return workspace_module, integration_module, engineering_state_module

    def test_each_workflow_button_has_connected_handler(self):
        workspace_module, _, _ = self._import_modules()

        workspace = workspace_module.create_configurator_v2_workspace()

        self.assertEqual(
            tuple(workspace.action_bar_region.action_handlers.keys()),
            workspace_module.ACTION_NAMES,
        )

    def test_clicking_validate_updates_validation_panel_and_message_state(self):
        workspace_module, integration_module, engineering_state_module = self._import_modules()
        from domain.base_cabinet_specification import BaseCabinetSpecification

        workspace = workspace_module.create_configurator_v2_workspace()
        integration_module.attach_service_integration(workspace)
        workspace.active_engineering_state = engineering_state_module.ActiveEngineeringState(
            specification=BaseCabinetSpecification()
        )

        validation_report = types.SimpleNamespace(
            violations=(
                types.SimpleNamespace(
                    rule_label="Width Rule",
                    violation_severity="ERROR",
                    violation_status="FAIL",
                    violation_message="Width is invalid",
                ),
            )
        )

        with patch(
            "domain.base_cabinet_specification_validation.validate_base_cabinet_specification",
            return_value=validation_report,
        ):
            workspace.action_bar_region.action_buttons["Validate"].click()

        validation_panel = next(
            panel for panel in workspace.review_panel_read_models
            if panel.panel_name == "Validation"
        )
        self.assertTrue(validation_panel.available)
        self.assertEqual(validation_panel.sections[0].section_name, "Errors")
        self.assertEqual(validation_panel.sections[0].rows[0][0], "Width Rule")
        self.assertIn(
            "Validation review completed",
            workspace.message_center_read_model.messages[-1].text,
        )
        self.assertIs(workspace.bottom_tabs.currentWidget(), workspace.review_region)
        self.assertEqual(workspace.review_region.tabs.currentIndex(), 0)

    def test_clicking_refresh_preview_uses_existing_preview_path(self):
        workspace_module, integration_module, _ = self._import_modules()

        workspace = workspace_module.create_configurator_v2_workspace()
        integration_module.attach_service_integration(workspace)
        selection = workspace_module.ConfiguratorSelection(
            selection_type="CABINET",
            selection_id="cabinet-1",
            display_name="Cabinet A",
            source_region="ProjectTreeRegion",
        )
        workspace.current_selection = selection
        starting_tab = workspace.bottom_tabs.currentWidget()

        workspace.action_bar_region.action_buttons["Refresh Preview"].click()

        self.assertEqual(workspace.preview_read_model.highlighted_item_id, "cabinet-1")
        self.assertEqual(workspace.preview_read_model.preview_state, "Ready")
        self.assertIs(workspace.bottom_tabs.currentWidget(), starting_tab)

    def test_buttons_without_backend_show_explicit_not_connected_message(self):
        workspace_module, integration_module, _ = self._import_modules()

        workspace = workspace_module.create_configurator_v2_workspace()
        integration_module.attach_service_integration(workspace)

        for action_name in (
            "Save Draft",
            "Generate Quotation",
            "Approve Release",
            "Export Production Documents",
        ):
            before = len(workspace.message_center_read_model.messages)
            workspace.action_bar_region.action_buttons[action_name].click()
            self.assertIn(
                "not connected yet",
                workspace.message_center_read_model.messages[-1].text.lower(),
            )
            self.assertGreater(
                len(workspace.message_center_read_model.messages),
                before,
            )
            self.assertIs(workspace.bottom_tabs.currentWidget(), workspace.message_center_region)

    def test_no_button_silently_does_nothing(self):
        workspace_module, integration_module, engineering_state_module = self._import_modules()
        from domain.base_cabinet_specification import BaseCabinetSpecification

        workspace = workspace_module.create_configurator_v2_workspace()
        integration_module.attach_service_integration(workspace)
        workspace.active_engineering_state = engineering_state_module.ActiveEngineeringState(
            specification=BaseCabinetSpecification()
        )

        with patch(
            "domain.base_cabinet_specification_validation.validate_base_cabinet_specification",
            return_value=types.SimpleNamespace(violations=()),
        ):
            before = len(workspace.message_center_read_model.messages)
            workspace.action_bar_region.action_buttons["Validate"].click()
            after = len(workspace.message_center_read_model.messages)

        self.assertGreater(after, before)

    def test_generate_manufacturing_activates_manufacturing_review_tab(self):
        workspace_module, integration_module, engineering_state_module = self._import_modules()

        workspace = workspace_module.create_configurator_v2_workspace()
        integration_module.attach_service_integration(workspace)
        workspace.active_engineering_state = engineering_state_module.ActiveEngineeringState(
            scene_graph=object(),
        )

        with patch.object(workspace.service_integration, "generate_manufacturing", return_value="ok"):
            workspace.action_bar_region.action_buttons["Generate Manufacturing"].click()

        self.assertIs(workspace.bottom_tabs.currentWidget(), workspace.review_region)
        self.assertEqual(workspace.review_region.tabs.currentIndex(), 1)

    def test_review_cost_activates_cost_review_tab(self):
        workspace_module, integration_module, _ = self._import_modules()

        workspace = workspace_module.create_configurator_v2_workspace()
        integration_module.attach_service_integration(workspace)

        with patch.object(workspace.service_integration, "review_cost", return_value="ok"):
            workspace.action_bar_region.action_buttons["Review Cost"].click()

        self.assertIs(workspace.bottom_tabs.currentWidget(), workspace.review_region)
        self.assertEqual(workspace.review_region.tabs.currentIndex(), 2)
