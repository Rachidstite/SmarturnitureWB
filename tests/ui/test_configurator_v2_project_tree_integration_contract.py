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

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text


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


class _FakeTabWidget(_FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tabs = []

    def addTab(self, widget, title):
        self.tabs.append((widget, title))


def _fake_qt_module():
    return types.SimpleNamespace(
        QtWidgets=types.SimpleNamespace(
            QWidget=_FakeWidget,
            QFrame=_FakeWidget,
            QVBoxLayout=_FakeLayout,
            QHBoxLayout=_FakeLayout,
            QFormLayout=_FakeLayout,
            QComboBox=_FakeComboBox,
            QPushButton=_FakeButton,
            QLabel=_FakeWidget,
            QTabWidget=_FakeTabWidget,
        ),
        QtCore=types.SimpleNamespace(),
    )


class TestConfiguratorV2ProjectTreeIntegrationContract(unittest.TestCase):
    def _import_modules(self):
        with patch.dict(
            sys.modules,
            {"core.qt_compat": _fake_qt_module()},
        ):
            workspace_module = importlib.import_module("ui.configurator_v2.workspace")
            integration_module = importlib.import_module("ui.configurator_v2.service_integration")
            adapters = importlib.import_module("ui.configurator_v2.projection_adapters")
            read_models = importlib.import_module("ui.configurator_v2.read_models")
        return workspace_module, integration_module, adapters, read_models

    def test_project_tree_region_accepts_read_model_and_renders_labels(self):
        workspace_module, _, adapters, read_models = self._import_modules()
        workspace = workspace_module.create_configurator_v2_workspace()

        read_model = adapters.build_project_tree_read_model(
            {
                "selected_node_id": "project-1",
                "customer": {"id": "customer-1", "label": "Customer A"},
                "project": {"id": "project-1", "label": "Project A", "state": "Draft"},
                "room": {"id": "room-1", "label": "Room A", "state": "Draft"},
                "wall": {"id": "wall-1", "label": "Wall A", "is_stale": True},
                "cabinet": {"id": "cabinet-1", "label": "Cabinet A", "is_supported": False},
                "documents": {"id": "docs-1", "label": "Documents"},
            }
        )

        workspace.set_project_tree_read_model(read_model)

        self.assertIsInstance(workspace.project_tree_read_model, read_models.ProjectTreeReadModel)
        self.assertEqual(workspace.project_tree_region.selected_node_id, "project-1")
        self.assertEqual(workspace.project_tree_region.read_model.selected_node_id, "project-1")
        self.assertTrue(any("Customer A" in row for row in workspace.project_tree_region.render_rows))
        self.assertTrue(any("Project A" in row for row in workspace.project_tree_region.render_rows))
        self.assertTrue(any("unsupported" in row for row in workspace.project_tree_region.render_rows))
        self.assertTrue(any("stale" in row for row in workspace.project_tree_region.render_rows))
        self.assertIn("cabinet-1", workspace.project_tree_region.node_metadata)
        self.assertEqual(workspace.project_tree_region.node_metadata["cabinet-1"]["is_supported"], "False")

    def test_selecting_tree_node_updates_workspace_selection(self):
        workspace_module, _, adapters, _ = self._import_modules()
        workspace = workspace_module.create_configurator_v2_workspace()
        workspace.set_project_tree_read_model(
            adapters.build_project_tree_read_model(
                {
                    "customer": {"id": "customer-1", "label": "Customer A"},
                    "project": {"id": "project-1", "label": "Project A", "state": "Draft"},
                }
            )
        )

        workspace.project_tree_region.select_node("project-1")

        self.assertEqual(workspace.current_selection.selection_type, "PROJECT")
        self.assertEqual(workspace.current_selection.selection_id, "project-1")
        self.assertEqual(workspace.current_selection.display_name, "Project A")
        self.assertEqual(workspace.inspector_region.selection_id_value.text(), "project-1")
        self.assertEqual(workspace.preview_region.highlighted_selection_id, "project-1")

    def test_refresh_project_tree_updates_workspace_and_region(self):
        workspace_module, integration_module, adapters, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings
        )
        workspace.set_project_context(
            current_customer={"label": "Customer A"},
            current_project={"label": "Project A"},
            current_product_family={"label": "Base Cabinet"},
            current_product={"label": "Cabinet A"},
        )
        integration = integration_module.attach_service_integration(workspace, bindings)

        read_model = integration.refresh_project_tree()

        self.assertEqual(workspace.project_tree_read_model, read_model)
        self.assertEqual(workspace.project_tree_region.read_model, read_model)
        self.assertTrue(any("Customer A" in row for row in workspace.project_tree_region.render_rows))
        bindings.project_application_service.execute.assert_not_called()
        bindings.engineering_application_service.execute.assert_not_called()
        bindings.manufacturing_application_service.execute.assert_not_called()

    def test_tree_selection_does_not_call_services_during_construction_or_selection(self):
        workspace_module, integration_module, adapters, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings
        )
        integration_module.attach_service_integration(workspace, bindings)
        workspace.set_project_tree_read_model(
            adapters.build_project_tree_read_model({"project": {"id": "project-1", "label": "Project A"}})
        )

        workspace.project_tree_region.select_node("project-1")

        bindings.project_application_service.execute.assert_not_called()
        bindings.engineering_application_service.execute.assert_not_called()
        bindings.manufacturing_application_service.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
