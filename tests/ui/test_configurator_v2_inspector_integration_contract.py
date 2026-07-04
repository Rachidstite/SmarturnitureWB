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


class TestConfiguratorV2InspectorIntegrationContract(unittest.TestCase):
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

    def test_inspector_accepts_read_model_and_groups_fields(self):
        workspace_module, _, adapters, read_models = self._import_modules()
        workspace = workspace_module.create_configurator_v2_workspace()

        inspector_rm = adapters.build_inspector_read_model(
            {
                "selection_id": "door-1",
                "selection_type": "DOOR",
                "display_name": "Left Door",
                "source_reference": "ProjectTreeRegion",
                "fields": [
                    {"name": "width", "label": "Width", "value": "600", "unit": "mm", "group": "Geometry"},
                    {"name": "finish", "label": "Finish", "value": "Oak", "group": "Materials"},
                    {"name": "hinge", "label": "Hinge", "value": "Soft close", "group": "Hardware"},
                ],
                "warnings": ["Check hinge offset"],
                "stale": True,
            }
        )

        workspace.set_inspector_read_model(inspector_rm)

        self.assertIsInstance(workspace.inspector_read_model, read_models.InspectorReadModel)
        self.assertIs(workspace.inspector_region.read_model, inspector_rm)
        self.assertIn("Selection Type: DOOR", workspace.inspector_region.render_rows)
        self.assertIn("Warnings: Check hinge offset", workspace.inspector_region.render_rows)
        self.assertEqual(len(workspace.inspector_region.group_field_labels["Geometry"]), 1)
        self.assertEqual(len(workspace.inspector_region.group_field_labels["Materials"]), 1)
        self.assertEqual(len(workspace.inspector_region.group_field_labels["Hardware"]), 1)

    def test_selection_updates_inspector_without_backend_calls(self):
        workspace_module, _, adapters, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        workspace.set_project_tree_read_model(
            adapters.build_project_tree_read_model(
                {
                    "project": {"id": "project-1", "label": "Project A"},
                }
            )
        )

        workspace.project_tree_region.select_node("project-1")

        self.assertEqual(workspace.current_selection.selection_id, "project-1")
        self.assertEqual(workspace.inspector_read_model.selection_id, "project-1")
        self.assertIn("Selection ID: project-1", workspace.inspector_region.render_rows)
        self.assertGreater(len(workspace.inspector_region.group_field_labels["Metadata"]), 0)
        bindings.project_application_service.execute.assert_not_called()
        bindings.engineering_application_service.execute.assert_not_called()
        bindings.manufacturing_application_service.execute.assert_not_called()

    def test_refresh_inspector_handles_unsupported_selection_safely(self):
        workspace_module, integration_module, _, read_models = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        read_model = integration.refresh_inspector(
            {
                "selection_id": "cabinet-1",
                "selection_type": "CABINET",
                "display_name": "Cabinet A",
                "source_reference": "ProjectTreeRegion",
                "unsupported": True,
                "unsupported_reason": "Selection is not executable yet",
                "suggested_action": "Select a supported cabinet family",
                "fields": [],
            }
        )

        self.assertIsInstance(read_model, read_models.InspectorReadModel)
        self.assertTrue(read_model.unsupported)
        self.assertIn("Unsupported Status: Unsupported", workspace.inspector_region.render_rows)
        self.assertIn("Unsupported Reason: Selection is not executable yet", workspace.inspector_region.render_rows)
        self.assertIn("Suggested Action: Select a supported cabinet family", workspace.inspector_region.render_rows)
        self.assertEqual(workspace.message_center_read_model.highest_severity, "UNSUPPORTED")
        bindings.project_application_service.execute.assert_not_called()
        bindings.engineering_application_service.execute.assert_not_called()
        bindings.manufacturing_application_service.execute.assert_not_called()

    def test_no_domain_imports_in_inspector_path(self):
        forbidden_modules = (
            "domain.base_cabinet_engineering_entry",
            "manufacturing.factory_release_package",
            "manufacturing.factory_decision_projection",
            "manufacturing.manufacturing_production_package",
            "commercial_outputs.commercial_package_report",
            "cost_intelligence.quotation_document",
        )
        for module_name in forbidden_modules:
            sys.modules.pop(module_name, None)

        self._import_modules()

        for module_name in forbidden_modules:
            self.assertNotIn(module_name, sys.modules)


if __name__ == "__main__":
    unittest.main()
