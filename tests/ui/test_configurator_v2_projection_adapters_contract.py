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


class TestConfiguratorV2ProjectionAdaptersContract(unittest.TestCase):
    def _import_modules(self):
        with patch.dict(
            sys.modules,
            {"core.qt_compat": _fake_qt_module()},
        ):
            read_models = importlib.import_module("ui.configurator_v2.read_models")
            adapters = importlib.import_module("ui.configurator_v2.projection_adapters")
            workspace = importlib.import_module("ui.configurator_v2.workspace")
        return read_models, adapters, workspace

    def test_adapter_module_exists_and_empty_inputs_are_safe(self):
        read_models, adapters, _ = self._import_modules()

        self.assertIsInstance(adapters.build_project_tree_read_model(), read_models.ProjectTreeReadModel)
        self.assertIsInstance(adapters.build_inspector_read_model(), read_models.InspectorReadModel)
        self.assertIsInstance(adapters.build_preview_read_model(), read_models.PreviewReadModel)
        self.assertIsInstance(adapters.build_message_center_read_model(), read_models.MessageCenterReadModel)

        review_models = adapters.build_review_panel_read_models()
        self.assertEqual(len(review_models), 5)
        self.assertEqual(
            [panel.panel_name for panel in review_models],
            ["Validation", "Manufacturing", "Cost", "Commercial", "Release"],
        )

    def test_dict_and_object_summaries_adapt_to_read_models(self):
        read_models, adapters, _ = self._import_modules()

        project_tree = adapters.build_project_tree_read_model(
            {
                "selected_node_id": "project-1",
                "expanded_node_ids": ["project-1"],
                "customer": {"id": "customer-1", "label": "Customer A"},
                "project": types.SimpleNamespace(node_id="project-1", name="Project A", state="Draft"),
                "room": {"label": "Room 1", "children": [{"label": "Wall A", "node_type": "WALL"}]},
                "documents": [{"label": "Quote.pdf", "node_type": "DOCUMENT"}],
            }
        )
        self.assertEqual(project_tree.selected_node_id, "project-1")
        self.assertEqual(project_tree.root_nodes[0].node_type, "PROJECT")
        self.assertEqual(project_tree.root_nodes[1].label, "Project A")
        self.assertEqual(project_tree.root_nodes[2].children[0].label, "Wall A")

        inspector = adapters.build_inspector_read_model(
            {
                "selection_id": "door-1",
                "selection_type": "DOOR",
                "display_name": "Left Door",
                "fields": [
                    {
                        "name": "width",
                        "label": "Width",
                        "value": "600",
                        "unit": "mm",
                        "editable": False,
                        "source_reference": "door-1",
                    }
                ],
                "warnings": ["Check hinge offset"],
                "stale": True,
            }
        )
        self.assertEqual(inspector.selection_type, "DOOR")
        self.assertEqual(inspector.fields[0].unit, "mm")
        self.assertTrue(inspector.stale)

        preview = adapters.build_preview_read_model(
            {
                "preview_mode": "Design View",
                "highlighted_item_id": "door-1",
                "items": [
                    {
                        "item_id": "door-1",
                        "item_type": "DOOR",
                        "label": "Left Door",
                        "visible": True,
                        "selected": True,
                        "display_metadata": [("role", "front")],
                        "source_reference": "preview-1",
                    }
                ],
                "stale": True,
                "unsupported_reason": "",
            }
        )
        self.assertEqual(preview.preview_mode, "Design View")
        self.assertEqual(preview.items[0].item_id, "door-1")
        self.assertTrue(preview.stale)

        message_center = adapters.build_message_center_read_model(
            {
                "messages": [
                    {"message_id": "m1", "severity": "INFO", "category": "General", "text": "ok"},
                    {"message_id": "m2", "severity": "STALE", "category": "Preview", "text": "stale"},
                    {"message_id": "m3", "severity": "BLOCKER", "category": "Release", "text": "blocked"},
                ]
            }
        )
        self.assertEqual(message_center.highest_severity, "BLOCKER")
        self.assertTrue(message_center.has_blockers)
        self.assertTrue(message_center.has_stale_outputs)

        review_panels = adapters.build_review_panel_read_models(
            {
                "panels": {
                    "Validation": {
                        "stale": True,
                        "available": True,
                        "sections": [
                            {
                                "section_name": "Summary",
                                "rows": [("status", "ready")],
                                "warnings": ["review fit"],
                                "source_reference": "validation-1",
                            }
                        ],
                    },
                    "Manufacturing": {"available": False, "sections": []},
                }
            }
        )
        self.assertEqual(review_panels[0].panel_name, "Validation")
        self.assertTrue(review_panels[0].stale)
        self.assertFalse(review_panels[1].available)

    def test_preview_adapter_rejects_backend_like_objects(self):
        _, adapters, _ = self._import_modules()

        class _FakeFreeCADObject:
            Shape = object()

        with self.assertRaises(TypeError):
            adapters.build_preview_read_model({"items": [_FakeFreeCADObject()]})

        class _FakeSceneGraphNode:
            ViewObject = object()

        with self.assertRaises(TypeError):
            adapters.build_preview_read_model(_FakeSceneGraphNode())

    def test_workspace_accepts_read_model_updates_without_service_calls(self):
        read_models, adapters, workspace_module = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings
        )

        workspace.set_project_tree_read_model(
            adapters.build_project_tree_read_model({"customer": {"label": "Customer A"}})
        )
        workspace.set_inspector_read_model(
            adapters.build_inspector_read_model(
                {
                    "selection_id": "door-1",
                    "selection_type": "DOOR",
                    "display_name": "Left Door",
                }
            )
        )
        workspace.set_preview_read_model(adapters.build_preview_read_model({}))
        workspace.set_message_center_read_model(
            adapters.build_message_center_read_model({"messages": []})
        )
        workspace.set_review_panel_read_models(
            adapters.build_review_panel_read_models({"panels": {}})
        )

        self.assertIsInstance(workspace.project_tree_read_model, read_models.ProjectTreeReadModel)
        self.assertIsInstance(workspace.inspector_read_model, read_models.InspectorReadModel)
        self.assertIsInstance(workspace.preview_read_model, read_models.PreviewReadModel)
        self.assertIsInstance(workspace.message_center_read_model, read_models.MessageCenterReadModel)
        self.assertEqual(len(workspace.review_panel_read_models), 5)

        bindings.project_application_service.execute.assert_not_called()
        bindings.engineering_application_service.execute.assert_not_called()
        bindings.manufacturing_application_service.execute.assert_not_called()

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
