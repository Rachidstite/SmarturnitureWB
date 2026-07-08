import importlib
import sys
import types
import unittest
from dataclasses import is_dataclass
from unittest.mock import Mock, patch

from application.application_service_result import ApplicationServiceResult


class _FakeSignal:
    def connect(self, _callback):
        self._callback = _callback
        return None

    def emit(self, *args, **kwargs):
        callback = getattr(self, "_callback", None)
        if callable(callback):
            return callback(*args, **kwargs)
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


class _FakeLineEdit(_FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editingFinished = _FakeSignal()


def _fake_qt_module():
    return types.SimpleNamespace(
        QtWidgets=types.SimpleNamespace(
            QWidget=_FakeWidget,
            QFrame=_FakeWidget,
            QVBoxLayout=_FakeLayout,
            QHBoxLayout=_FakeLayout,
            QFormLayout=_FakeLayout,
            QComboBox=_FakeComboBox,
            QLineEdit=_FakeLineEdit,
            QPushButton=_FakeButton,
            QLabel=_FakeWidget,
            QTabWidget=_FakeTabWidget,
        ),
        QtCore=types.SimpleNamespace(),
    )


class _FakeNode:
    def __init__(self, node_id, label, role_name, x, y, z, width, depth, height):
        self.identity = types.SimpleNamespace(key=node_id)
        self.node_type = role_name
        self.label = label
        self.name = label
        self.visible = True
        self.selectable = True
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.depth = depth
        self.height = height
        self.material = "MDF_18MM"
        self.metadata = {"display_name": label}
        self.role = types.SimpleNamespace(name=role_name)


class _FakeSceneGraph:
    def __init__(self, nodes):
        self._nodes = list(nodes)

    def all_nodes(self):
        return list(self._nodes)


class TestConfiguratorV2ServiceIntegrationContract(unittest.TestCase):
    def _import_modules(self):
        with patch.dict(
            sys.modules,
            {"core.qt_compat": _fake_qt_module()},
        ):
            engineering_state = importlib.import_module(
                "ui.configurator_v2.engineering_state"
            )
            workspace_module = importlib.import_module("ui.configurator_v2.workspace")
            integration_module = importlib.import_module("ui.configurator_v2.service_integration")
            read_models = importlib.import_module("ui.configurator_v2.read_models")
            adapters = importlib.import_module("ui.configurator_v2.projection_adapters")
        return engineering_state, workspace_module, integration_module, read_models, adapters

    def test_module_exists_and_constructor_is_side_effect_free(self):
        _, workspace_module, integration_module, _, _ = self._import_modules()
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
        _, workspace_module, integration_module, read_models, adapters = self._import_modules()
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
        _, workspace_module, integration_module, read_models, _ = self._import_modules()
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
        _, workspace_module, integration_module, read_models, adapters = self._import_modules()
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

    def test_active_engineering_state_is_passive_dataclass(self):
        engineering_state, _, _, _, _ = self._import_modules()

        self.assertTrue(is_dataclass(engineering_state.ActiveEngineeringState))

        state = engineering_state.ActiveEngineeringState()

        self.assertEqual(state.family, "")
        self.assertIsNone(state.specification)
        self.assertIsNone(state.cabinet)
        self.assertIsNone(state.scene_graph)
        self.assertEqual(state.metadata, {})
        self.assertFalse(state.engineering_dirty)
        self.assertFalse(state.manufacturing_stale)
        self.assertFalse(state.cost_stale)
        self.assertFalse(state.commercial_stale)

    def test_workspace_runtime_debug_snapshot_reports_identity_and_inspector_state(self):
        _, workspace_module, _, _, _ = self._import_modules()

        workspace = workspace_module.create_configurator_v2_workspace()
        snapshot = workspace.runtime_debug_snapshot()

        self.assertIn("workspace_id", snapshot)
        self.assertIn("runtime_debug_id", snapshot)
        self.assertTrue(snapshot["runtime_debug_id"].startswith("cv2ws-"))
        self.assertTrue(snapshot["has_active_engineering_state"])
        self.assertFalse(snapshot["has_specification"])
        self.assertEqual(snapshot["inspector_field_names"], ())
        self.assertEqual(snapshot["editable_field_input_keys"], ())

    def test_workspace_initializes_active_engineering_state(self):
        engineering_state, workspace_module, _, _, _ = self._import_modules()

        workspace = workspace_module.create_configurator_v2_workspace()

        self.assertIsInstance(
            workspace.active_engineering_state,
            engineering_state.ActiveEngineeringState,
        )
        self.assertEqual(workspace.active_engineering_state.family, "")

    def test_create_base_cabinet_updates_preview_read_model(self):
        _, workspace_module, integration_module, read_models, _ = self._import_modules()
        scene_graph = _FakeSceneGraph(
            [
                _FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 600.0, 580.0, 720.0),
                _FakeNode("door-1", "Door", "DOOR_PANEL", 18.0, 0.0, 0.0, 280.0, 18.0, 700.0),
            ]
        )
        engineering_service = Mock()
        engineering_service.execute.return_value = ApplicationServiceResult(
            success=True,
            data={
                "cabinet": types.SimpleNamespace(graph=scene_graph, scene_graph=scene_graph),
                "specification": types.SimpleNamespace(width_mm=600.0, height_mm=720.0, depth_mm=580.0),
                "metadata": {"material": "MDF"},
            },
            errors=(),
            diagnostics=(),
        )
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=engineering_service,
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings
        )
        integration = integration_module.attach_service_integration(workspace, bindings)

        preview = integration.create_base_cabinet()

        self.assertIsInstance(preview, read_models.PreviewReadModel)
        self.assertTrue(preview.scene_available)
        self.assertEqual(preview.preview_title, "Base Cabinet")
        self.assertEqual(preview.current_family, "Base Cabinet")
        self.assertEqual(preview.node_count, 2)
        self.assertEqual(workspace.preview_read_model, preview)
        self.assertEqual(workspace.current_product_family, "Base Cabinet")
        self.assertEqual(workspace.current_product, "Base Cabinet")
        engineering_service.execute.assert_called_once_with()

    def test_create_base_cabinet_stores_active_engineering_state(self):
        _, workspace_module, integration_module, _, _ = self._import_modules()
        scene_graph = _FakeSceneGraph(
            [
                _FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 600.0, 580.0, 720.0),
            ]
        )
        specification = types.SimpleNamespace(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
        )
        cabinet = types.SimpleNamespace(graph=scene_graph, scene_graph=scene_graph)
        metadata = {"material": "MDF", "sku": "BC-600"}
        engineering_service = Mock()
        engineering_service.execute.return_value = ApplicationServiceResult(
            success=True,
            data={
                "cabinet": cabinet,
                "specification": specification,
                "metadata": metadata,
            },
            errors=(),
            diagnostics=(),
        )
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=engineering_service,
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings
        )
        integration = integration_module.attach_service_integration(workspace, bindings)

        integration.create_base_cabinet()

        state = workspace.active_engineering_state
        self.assertEqual(state.family, "Base Cabinet")
        self.assertIs(state.specification, specification)
        self.assertIs(state.cabinet, cabinet)
        self.assertIs(state.scene_graph, scene_graph)
        self.assertEqual(state.metadata, metadata)
        self.assertFalse(state.engineering_dirty)
        self.assertTrue(state.manufacturing_stale)
        self.assertTrue(state.cost_stale)
        self.assertTrue(state.commercial_stale)

    def test_create_base_cabinet_populates_editable_inspector_fields(self):
        """Base cabinet creation must expose engineering fields to the inspector."""
        _, workspace_module, integration_module, read_models, _ = self._import_modules()
        scene_graph = _FakeSceneGraph(
            [
                _FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 600.0, 580.0, 720.0),
                _FakeNode("divider-1", "Divider", "DIVIDER", 194.0, 0.0, 98.0, 18.0, 552.0, 604.0),
            ]
        )
        specification = types.SimpleNamespace(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
            shelf_count=3,
            door_count=2,
        )
        cabinet = types.SimpleNamespace(graph=scene_graph, scene_graph=scene_graph)
        engineering_service = Mock()
        engineering_service.execute.return_value = ApplicationServiceResult(
            success=True,
            data={
                "cabinet": cabinet,
                "specification": specification,
                "metadata": {"material": "MDF", "sku": "BC-600"},
            },
            errors=(),
            diagnostics=(),
        )
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=engineering_service,
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        integration.create_base_cabinet()

        self.assertIs(workspace.active_engineering_state.specification, specification)
        self.assertIsInstance(workspace.inspector_read_model, read_models.InspectorReadModel)
        self.assertEqual(
            [field.name for field in workspace.inspector_read_model.fields[:5]],
            ["width_mm", "height_mm", "depth_mm", "shelf_count", "door_count"],
        )
        self.assertEqual(
            workspace.inspector_read_model.fields[0].source_reference,
            "ActiveEngineeringState.specification",
        )
        self.assertIn("width_mm", workspace.inspector_region.editable_field_inputs)
        self.assertIn("height_mm", workspace.inspector_region.editable_field_inputs)
        self.assertIn("depth_mm", workspace.inspector_region.editable_field_inputs)
        self.assertIn("shelf_count", workspace.inspector_region.editable_field_inputs)
        self.assertIn("door_count", workspace.inspector_region.editable_field_inputs)
        self.assertEqual(workspace.inspector_region.editable_field_inputs["width_mm"].text(), "600.0")
        self.assertEqual(workspace.inspector_region.editable_field_inputs["height_mm"].text(), "720.0")
        self.assertEqual(workspace.inspector_region.editable_field_inputs["depth_mm"].text(), "580.0")
        self.assertEqual(workspace.inspector_region.editable_field_inputs["shelf_count"].text(), "3")
        self.assertEqual(workspace.inspector_region.editable_field_inputs["door_count"].text(), "2")
        self.assertTrue(any("Width: 600.0 mm" in row for row in workspace.inspector_region.render_rows))
        self.assertTrue(any("Height: 720.0 mm" in row for row in workspace.inspector_region.render_rows))
        self.assertTrue(any("Depth: 580.0 mm" in row for row in workspace.inspector_region.render_rows))
        self.assertTrue(any("Shelf Count: 3" in row for row in workspace.inspector_region.render_rows))
        self.assertTrue(any("Door Count: 2" in row for row in workspace.inspector_region.render_rows))

    def test_create_base_cabinet_uses_active_engineering_state_not_preview_as_source_of_truth(self):
        _, workspace_module, integration_module, _, _ = self._import_modules()
        scene_graph = _FakeSceneGraph(
            [
                _FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 600.0, 580.0, 720.0),
            ]
        )
        specification = types.SimpleNamespace(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
        )
        cabinet = types.SimpleNamespace(graph=scene_graph, scene_graph=scene_graph)
        engineering_service = Mock()
        engineering_service.execute.return_value = ApplicationServiceResult(
            success=True,
            data={
                "cabinet": cabinet,
                "specification": specification,
                "metadata": {"material": "MDF"},
            },
            errors=(),
            diagnostics=(),
        )
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=engineering_service,
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings
        )
        integration = integration_module.attach_service_integration(workspace, bindings)

        preview = integration.create_base_cabinet()

        self.assertIs(workspace.active_engineering_state.scene_graph, scene_graph)
        self.assertIs(workspace.active_engineering_state.specification, specification)
        self.assertEqual(preview.node_count, 1)
        self.assertNotEqual(workspace.active_engineering_state.scene_graph, preview)

    def test_update_active_base_cabinet_width_regenerates_engineering(self):
        _, workspace_module, integration_module, read_models, _ = self._import_modules()
        initial_specification = types.SimpleNamespace(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
        )
        updated_specification = types.SimpleNamespace(
            width_mm=800.0,
            height_mm=720.0,
            depth_mm=580.0,
        )
        updated_scene_graph = _FakeSceneGraph(
            [
                _FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 800.0, 580.0, 720.0),
                _FakeNode("door-1", "Door", "DOOR_PANEL", 18.0, 0.0, 0.0, 380.0, 18.0, 700.0),
            ]
        )
        engineering_service = Mock()
        engineering_service.execute.side_effect = [
            ApplicationServiceResult(
                success=True,
                data={
                    "cabinet": types.SimpleNamespace(
                        graph=_FakeSceneGraph(
                            [_FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 600.0, 580.0, 720.0)]
                        ),
                        scene_graph=_FakeSceneGraph(
                            [_FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 600.0, 580.0, 720.0)]
                        ),
                    ),
                    "specification": initial_specification,
                    "metadata": {"material": "MDF"},
                },
                errors=(),
                diagnostics=(),
            ),
            ApplicationServiceResult(
                success=True,
                data={
                    "cabinet": types.SimpleNamespace(
                        graph=updated_scene_graph,
                        scene_graph=updated_scene_graph,
                    ),
                    "specification": updated_specification,
                    "metadata": {"material": "MDF", "sku": "BC-800"},
                },
                errors=(),
                diagnostics=(),
            ),
        ]
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=engineering_service,
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings
        )
        integration = integration_module.attach_service_integration(workspace, bindings)

        integration.create_base_cabinet()
        preview = integration.update_active_base_cabinet_width(800.0)

        self.assertIsInstance(preview, read_models.PreviewReadModel)
        self.assertEqual(engineering_service.execute.call_count, 2)
        self.assertEqual(initial_specification.width_mm, 600.0)
        self.assertEqual(
            engineering_service.execute.call_args_list[1].kwargs["specification"].width_mm,
            800.0,
        )
        self.assertEqual(workspace.active_engineering_state.specification.width_mm, 800.0)
        self.assertEqual(workspace.active_engineering_state.metadata["sku"], "BC-800")

    def test_update_active_base_cabinet_width_refreshes_preview(self):
        _, workspace_module, integration_module, _, _ = self._import_modules()
        initial_scene_graph = _FakeSceneGraph(
            [
                _FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 600.0, 580.0, 720.0),
            ]
        )
        updated_scene_graph = _FakeSceneGraph(
            [
                _FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 820.0, 580.0, 720.0),
                _FakeNode("door-1", "Door", "DOOR_PANEL", 18.0, 0.0, 0.0, 390.0, 18.0, 700.0),
            ]
        )
        engineering_service = Mock()
        engineering_service.execute.side_effect = [
            ApplicationServiceResult(
                success=True,
                data={
                    "cabinet": types.SimpleNamespace(graph=initial_scene_graph, scene_graph=initial_scene_graph),
                    "specification": types.SimpleNamespace(width_mm=600.0, height_mm=720.0, depth_mm=580.0),
                    "metadata": {},
                },
                errors=(),
                diagnostics=(),
            ),
            ApplicationServiceResult(
                success=True,
                data={
                    "cabinet": types.SimpleNamespace(graph=updated_scene_graph, scene_graph=updated_scene_graph),
                    "specification": types.SimpleNamespace(width_mm=820.0, height_mm=720.0, depth_mm=580.0),
                    "metadata": {},
                },
                errors=(),
                diagnostics=(),
            ),
        ]
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=engineering_service,
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings
        )
        integration = integration_module.attach_service_integration(workspace, bindings)

        first_preview = integration.create_base_cabinet()
        second_preview = integration.update_active_base_cabinet_width(820.0)

        self.assertEqual(first_preview.node_count, 1)
        self.assertEqual(second_preview.node_count, 2)
        self.assertEqual(workspace.preview_read_model, second_preview)
        self.assertEqual(workspace.active_engineering_state.scene_graph, updated_scene_graph)

    def test_update_active_base_cabinet_width_keeps_downstream_outputs_stale(self):
        _, workspace_module, integration_module, _, _ = self._import_modules()
        engineering_service = Mock()
        engineering_service.execute.side_effect = [
            ApplicationServiceResult(
                success=True,
                data={
                    "cabinet": types.SimpleNamespace(
                        graph=_FakeSceneGraph(
                            [_FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 600.0, 580.0, 720.0)]
                        ),
                        scene_graph=_FakeSceneGraph(
                            [_FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 600.0, 580.0, 720.0)]
                        ),
                    ),
                    "specification": types.SimpleNamespace(width_mm=600.0, height_mm=720.0, depth_mm=580.0),
                    "metadata": {},
                },
                errors=(),
                diagnostics=(),
            ),
            ApplicationServiceResult(
                success=True,
                data={
                    "cabinet": types.SimpleNamespace(
                        graph=_FakeSceneGraph(
                            [_FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 750.0, 580.0, 720.0)]
                        ),
                        scene_graph=_FakeSceneGraph(
                            [_FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 750.0, 580.0, 720.0)]
                        ),
                    ),
                    "specification": types.SimpleNamespace(width_mm=750.0, height_mm=720.0, depth_mm=580.0),
                    "metadata": {},
                },
                errors=(),
                diagnostics=(),
            ),
        ]
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=engineering_service,
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings
        )
        integration = integration_module.attach_service_integration(workspace, bindings)

        integration.create_base_cabinet()
        integration.update_active_base_cabinet_width(750.0)

        state = workspace.active_engineering_state
        self.assertFalse(state.engineering_dirty)
        self.assertTrue(state.manufacturing_stale)
        self.assertTrue(state.cost_stale)
        self.assertTrue(state.commercial_stale)

    def test_create_base_cabinet_does_not_import_backend_modules_into_ui(self):
        _, workspace_module, integration_module, _, _ = self._import_modules()
        forbidden_modules = (
            "domain.base_cabinet_engineering_entry",
            "engine.cabinet_builder",
            "scene_graph.renderer",
            "FreeCAD",
            "FreeCADGui",
            "Part",
        )
        for module_name in forbidden_modules:
            sys.modules.pop(module_name, None)

        engineering_service = Mock()
        engineering_service.execute.return_value = ApplicationServiceResult(
            success=True,
            data={
                "cabinet": types.SimpleNamespace(
                    graph=_FakeSceneGraph(
                        [_FakeNode("cabinet-1", "Cabinet", "CABINET", 0.0, 0.0, 0.0, 600.0, 580.0, 720.0)]
                    )
                ),
                "specification": types.SimpleNamespace(width_mm=600.0, height_mm=720.0, depth_mm=580.0),
                "metadata": {},
            },
            errors=(),
            diagnostics=(),
        )
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=engineering_service,
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(
            service_bindings=bindings
        )
        integration = integration_module.attach_service_integration(workspace, bindings)

        integration.create_base_cabinet()

        for module_name in forbidden_modules:
            self.assertNotIn(module_name, sys.modules)

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
