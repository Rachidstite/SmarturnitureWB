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

    def setCurrentText(self, text):
        self._text = text


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


class TestConfiguratorV2PreviewIntegrationContract(unittest.TestCase):
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

    def test_preview_accepts_read_model_and_renders_metadata(self):
        workspace_module, _, adapters, read_models = self._import_modules()
        workspace = workspace_module.create_configurator_v2_workspace()

        preview_rm = adapters.build_preview_read_model(
            {
                "preview_title": "Base Cabinet Preview",
                "preview_mode": "Design View",
                "preview_state": "Ready",
                "current_family": "Base Cabinet",
                "highlighted_item_id": "cabinet-1",
                "highlighted_item_type": "CABINET",
                "viewport_message": "Focus on cabinet-1",
                "available_representations": ["Customer View", "Design View"],
                "warnings": ["Preview data is approximate"],
                "items": [
                    {
                        "item_id": "cabinet-1",
                        "item_type": "CABINET",
                        "label": "Cabinet A",
                        "visible": True,
                        "selected": True,
                        "display_metadata": [("role", "primary")],
                        "source_reference": "Selection",
                        "representation": "Selection Focus",
                    }
                ],
            }
        )

        workspace.set_preview_read_model(preview_rm)

        self.assertIsInstance(workspace.preview_read_model, read_models.PreviewReadModel)
        self.assertIs(workspace.preview_region.read_model, preview_rm)
        self.assertIn("Preview Title: Base Cabinet Preview", workspace.preview_region.render_rows)
        self.assertIn("Current Family: Base Cabinet", workspace.preview_region.render_rows)
        self.assertIn("Representation Availability: Customer View, Design View", workspace.preview_region.render_rows)
        self.assertIn("Viewport Message: Focus on cabinet-1", workspace.preview_region.render_rows)
        self.assertEqual(workspace.preview_region.highlighted_selection_id, "cabinet-1")
        self.assertEqual(workspace.preview_region.highlighted_selection_type, "CABINET")

    def test_selection_updates_preview_without_backend_calls(self):
        workspace_module, _, adapters, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        workspace.set_project_context(current_product_family="Base Cabinet")

        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="cabinet-1",
                display_name="Cabinet A",
                source_region="ProjectTreeRegion",
                metadata={"tree_node": "cabinet-1"},
            )
        )

        self.assertEqual(workspace.preview_read_model.current_family, "Base Cabinet")
        self.assertEqual(workspace.preview_read_model.highlighted_item_id, "cabinet-1")
        self.assertEqual(workspace.preview_region.highlighted_selection_id, "cabinet-1")
        self.assertEqual(workspace.preview_region.highlighted_selection_type, "CABINET")
        self.assertIn("Preview State: Ready", workspace.preview_region.render_rows)
        self.assertIn("Current Object: cabinet-1", workspace.preview_region.render_rows)
        bindings.project_application_service.execute.assert_not_called()
        bindings.engineering_application_service.execute.assert_not_called()
        bindings.manufacturing_application_service.execute.assert_not_called()

    def test_refresh_preview_updates_workspace_and_handles_unsupported_state(self):
        workspace_module, integration_module, adapters, read_models = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        workspace.set_project_context(current_product_family="Base Cabinet")
        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="cabinet-1",
                display_name="Cabinet A",
                source_region="ProjectTreeRegion",
            )
        )
        integration = integration_module.attach_service_integration(workspace, bindings)

        read_model = integration.refresh_preview(
            {
                "selection": workspace.current_selection,
                "current_family": "Base Cabinet",
                "preview_title": "Base Cabinet Preview",
                "preview_state": "Ready",
                "highlighted_item_id": "cabinet-1",
                "highlighted_item_type": "CABINET",
                "viewport_message": "Focus on Cabinet A",
                "available_representations": ["Customer View"],
                "warnings": [],
            }
        )

        self.assertIsInstance(read_model, read_models.PreviewReadModel)
        self.assertEqual(workspace.preview_read_model, read_model)
        self.assertEqual(workspace.preview_region.read_model, read_model)
        self.assertIn("Preview Title: Base Cabinet Preview", workspace.preview_region.render_rows)

        unsupported = integration.refresh_preview(
            {
                "preview_title": "Base Cabinet Preview",
                "unsupported_reason": "Preview integration not available yet",
            }
        )

        self.assertEqual(unsupported.unsupported_reason, "Preview integration not available yet")
        self.assertEqual(workspace.message_center_read_model.highest_severity, "UNSUPPORTED")

    def test_no_backend_renderer_or_domain_imports_in_preview_path(self):
        forbidden_modules = (
            "domain.base_cabinet_engineering_entry",
            "manufacturing.factory_release_package",
            "manufacturing.factory_decision_projection",
            "manufacturing.manufacturing_production_package",
            "commercial_outputs.commercial_package_report",
            "cost_intelligence.quotation_document",
            "gui.renderer",
            "FreeCAD",
            "FreeCADGui",
        )
        for module_name in forbidden_modules:
            sys.modules.pop(module_name, None)

        self._import_modules()

        for module_name in forbidden_modules:
            self.assertNotIn(module_name, sys.modules)


if __name__ == "__main__":
    unittest.main()
