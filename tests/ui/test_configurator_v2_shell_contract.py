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

    def addTab(self, widget, title):
        self.tabs.append((widget, title))


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
            return importlib.import_module("ui.configurator_v2.workspace")

    def test_shell_can_be_imported_and_constructed(self):
        module = self._import_workspace_module()

        workspace = module.create_configurator_v2_workspace()

        self.assertEqual(workspace.workspace_areas, module.WORKSPACE_AREAS)
        self.assertEqual(workspace.action_names, module.ACTION_NAMES)
        self.assertEqual(workspace.preview_modes, module.PREVIEW_MODES)
        self.assertEqual(workspace.review_panel_names, module.REVIEW_PANEL_NAMES)
        self.assertEqual(workspace.message_categories, module.MESSAGE_CATEGORIES)
        self.assertTrue(hasattr(workspace, "navigation_panel"))
        self.assertTrue(hasattr(workspace, "project_tree_panel"))
        self.assertTrue(hasattr(workspace, "preview_panel"))
        self.assertTrue(hasattr(workspace, "inspector_panel"))
        self.assertTrue(hasattr(workspace, "review_panels"))
        self.assertTrue(hasattr(workspace, "message_center"))
        self.assertTrue(hasattr(workspace, "action_bar"))

    def test_action_names_exist_and_buttons_are_disabled(self):
        module = self._import_workspace_module()
        workspace = module.create_configurator_v2_workspace()

        self.assertEqual(
            tuple(workspace.action_bar.action_buttons.keys()),
            module.ACTION_NAMES,
        )
        self.assertTrue(
            all(
                not getattr(button, "_enabled", True)
                for button in workspace.action_bar.action_buttons.values()
            )
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

    def test_legacy_configurator_still_imports(self):
        with patch.dict(
            sys.modules,
            _fake_runtime_modules() | {"core.qt_compat": _fake_qt_module()},
        ):
            legacy_module = importlib.import_module("ui.main_window")

        self.assertTrue(hasattr(legacy_module, "UIManager"))


if __name__ == "__main__":
    unittest.main()
