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


class TestConfiguratorV2ServiceIntegrationContract(unittest.TestCase):
    def _import_modules(self):
        with patch.dict(
            sys.modules,
            {"core.qt_compat": _fake_qt_module()},
        ):
            workspace_module = importlib.import_module("ui.configurator_v2.workspace")
            integration_module = importlib.import_module("ui.configurator_v2.service_integration")
            read_models = importlib.import_module("ui.configurator_v2.read_models")
            adapters = importlib.import_module("ui.configurator_v2.projection_adapters")
        return workspace_module, integration_module, read_models, adapters

    def test_module_exists_and_constructor_is_side_effect_free(self):
        workspace_module, integration_module, _, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings
        )
        integration = integration_module.ConfiguratorV2ServiceIntegration(
            workspace=workspace,
            service_bindings=bindings,
        )

        self.assertIs(integration.workspace, workspace)
        self.assertIs(integration.service_bindings, bindings)
        bindings.project_application_service.execute.assert_not_called()
        bindings.engineering_application_service.execute.assert_not_called()
        bindings.manufacturing_application_service.execute.assert_not_called()

    def test_refresh_project_tree_updates_read_model_without_service_calls(self):
        workspace_module, integration_module, read_models, adapters = self._import_modules()
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
        integration = integration_module.attach_service_integration(
            workspace,
            bindings,
        )

        read_model = integration.refresh_project_tree()

        self.assertIsInstance(read_model, read_models.ProjectTreeReadModel)
        self.assertIsInstance(workspace.project_tree_read_model, read_models.ProjectTreeReadModel)
        self.assertGreaterEqual(len(workspace.project_tree_read_model.root_nodes), 2)
        self.assertEqual(workspace.project_tree_read_model.root_nodes[0].label, "Customer A")
        self.assertEqual(workspace.project_tree_read_model.root_nodes[1].label, "Project A")
        bindings.project_application_service.execute.assert_not_called()
        bindings.engineering_application_service.execute.assert_not_called()
        bindings.manufacturing_application_service.execute.assert_not_called()

    def test_unsupported_refreshes_create_safe_messages(self):
        workspace_module, integration_module, read_models, _ = self._import_modules()
        workspace = workspace_module.create_configurator_v2_workspace()
        integration = integration_module.attach_service_integration(workspace)

        preview = integration.refresh_preview()
        validation = integration.refresh_validation()
        release = integration.refresh_release_review()

        self.assertIsInstance(preview, read_models.PreviewReadModel)
        self.assertEqual(preview.unsupported_reason, "Preview integration not available yet")
        self.assertIsInstance(validation, tuple)
        self.assertEqual(len(validation), 5)
        self.assertIsInstance(release, tuple)
        self.assertEqual(workspace.message_center_read_model.highest_severity, "UNSUPPORTED")
        self.assertGreaterEqual(len(workspace.message_center_read_model.messages), 3)

    def test_workspace_hook_and_setters_remain_safe(self):
        workspace_module, integration_module, read_models, adapters = self._import_modules()
        workspace = workspace_module.create_configurator_v2_workspace()
        integration = integration_module.attach_service_integration(workspace)

        self.assertIs(workspace.service_integration, integration)

        tree_rm = adapters.build_project_tree_read_model({"project": {"label": "Project X"}})
        inspector_rm = adapters.build_inspector_read_model({"selection_type": "PROJECT"})
        preview_rm = adapters.build_preview_read_model({"highlighted_item_id": "project-x"})
        message_rm = adapters.build_message_center_read_model({"messages": []})
        review_rm = adapters.build_review_panel_read_models({"panels": {}})

        workspace.set_project_tree_read_model(tree_rm)
        workspace.set_inspector_read_model(inspector_rm)
        workspace.set_preview_read_model(preview_rm)
        workspace.set_message_center_read_model(message_rm)
        workspace.set_review_panel_read_models(review_rm)

        self.assertIs(workspace.project_tree_read_model, tree_rm)
        self.assertIs(workspace.inspector_read_model, inspector_rm)
        self.assertIs(workspace.preview_read_model, preview_rm)
        self.assertIs(workspace.message_center_read_model, message_rm)
        self.assertEqual(workspace.review_panel_read_models, review_rm)

    def test_no_ui_widget_imports_backend_internals(self):
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
