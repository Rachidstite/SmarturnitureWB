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

    # ── Alpha-UI-7.1 — Preview Synchronization Contract Tests ─────

    def _make_mock_scene_node(self, node_id, width=800.0, height=900.0, depth=580.0):
        """Create a scene graph node source for the projection pipeline."""
        return types.SimpleNamespace(
            node_id=node_id,
            id=node_id,
            node_type="PANEL",
            type="PANEL",
            role=types.SimpleNamespace(name="PANEL"),
            label=f"Panel {node_id}",
            display_name=f"Panel {node_id}",
            name=f"Panel {node_id}",
            width=width,
            height=height,
            depth=depth,
            x=0.0, y=0.0, z=0.0,
            visible=True,
            selectable=True,
            transform=None,
            display_metadata={},
            metadata={},
            source_reference="mock",
            children=(),
        )

    def _make_mock_scene_graph(self, node_count=5, width=800.0, height=900.0, depth=580.0):
        """Create a mock scene graph with *node_count* nodes all sharing the
        same *width*, *height*, *depth* so the union bounds are predictable."""
        nodes = [
            self._make_mock_scene_node(f"node-{i}", width, height, depth)
            for i in range(node_count)
        ]
        scene_graph = Mock()
        scene_graph.all_nodes = lambda: nodes
        return scene_graph

    def _make_mock_result_from_scene_graph(self, scene_graph, width=800.0, height=900.0, depth=580.0, shelf_count=3, door_count=2):
        """Build an engineering-service result containing *scene_graph*
        and a matching specification."""
        spec = types.SimpleNamespace(
            width_mm=width, height_mm=height, depth_mm=depth,
            shelf_count=shelf_count, door_count=door_count,
        )
        cabinet = types.SimpleNamespace(scene_graph=scene_graph)
        result = Mock()
        result.data = {"cabinet": cabinet, "specification": spec, "metadata": {}}
        result.errors = ()
        result.diagnostics = ()
        return result

    def _make_engineering_state(self, spec, workspace_module):
        """Create an ActiveEngineeringState without importing domain."""
        return workspace_module.ActiveEngineeringState(
            family="Base Cabinet",
            specification=spec,
            cabinet=None,
            scene_graph=None,
        )

    def _make_specification(self, width=800.0, height=900.0, depth=580.0, shelf_count=3, door_count=2):
        return types.SimpleNamespace(
            width_mm=width, height_mm=height, depth_mm=depth,
            shelf_count=shelf_count, door_count=door_count,
        )

    def _baseline_scene_bounds_label(self, width=800.0, height=900.0, depth=580.0):
        """Return the expected scene_bounds label for uniform nodes
        placed at the origin."""
        return f"min=(0.0, 0.0, 0.0) max=({width}, {depth}, {height})"

    def test_width_edit_changes_preview_scene_bounds(self):
        """After width edit, PreviewReadModel scene_bounds must reflect
        the new width."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        sg_before = self._make_mock_scene_graph(node_count=5, width=800.0, height=900.0, depth=580.0)
        sg_after = self._make_mock_scene_graph(node_count=5, width=900.0, height=900.0, depth=580.0)
        spec_before = self._make_specification(width=800.0)

        eng_service.execute.return_value = self._make_mock_result_from_scene_graph(
            sg_after, width=900.0,
        )
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        workspace.active_engineering_state = self._make_engineering_state(spec_before, workspace_module)

        integration.update_active_base_cabinet_width(900.0)

        expected_bounds = self._baseline_scene_bounds_label(width=900.0)
        self.assertIn(
            expected_bounds, workspace.preview_read_model.scene_bounds,
            f"Expected scene_bounds '{expected_bounds}' after width edit, "
            f"got '{workspace.preview_read_model.scene_bounds}'",
        )

    def test_height_edit_changes_preview_scene_bounds(self):
        """After height edit, PreviewReadModel scene_bounds must reflect
        the new height."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        sg_after = self._make_mock_scene_graph(node_count=5, width=800.0, height=1200.0, depth=580.0)
        spec_before = self._make_specification(height=900.0)
        eng_service.execute.return_value = self._make_mock_result_from_scene_graph(
            sg_after, height=1200.0,
        )
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        workspace.active_engineering_state = self._make_engineering_state(spec_before, workspace_module)

        integration.update_active_base_cabinet_height(1200.0)

        expected_bounds = self._baseline_scene_bounds_label(height=1200.0)
        self.assertIn(
            expected_bounds, workspace.preview_read_model.scene_bounds,
        )

    def test_depth_edit_changes_preview_scene_bounds(self):
        """After depth edit, PreviewReadModel scene_bounds must reflect
        the new depth."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        sg_after = self._make_mock_scene_graph(node_count=5, width=800.0, height=900.0, depth=700.0)
        spec_before = self._make_specification(depth=580.0)
        eng_service.execute.return_value = self._make_mock_result_from_scene_graph(
            sg_after, depth=700.0,
        )
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        workspace.active_engineering_state = self._make_engineering_state(spec_before, workspace_module)

        integration.update_active_base_cabinet_depth(700.0)

        expected_bounds = self._baseline_scene_bounds_label(depth=700.0)
        self.assertIn(
            expected_bounds, workspace.preview_read_model.scene_bounds,
        )

    def test_shelf_count_edit_changes_preview_node_count(self):
        """After shelf_count edit, PreviewReadModel node_count must
        reflect the new number of scene nodes."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        # 3 nodes when shelf_count=1, 8 nodes when shelf_count=4
        sg_after = self._make_mock_scene_graph(node_count=8)
        spec_before = self._make_specification(shelf_count=1)
        eng_service.execute.return_value = self._make_mock_result_from_scene_graph(
            sg_after, shelf_count=4,
        )
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        workspace.active_engineering_state = self._make_engineering_state(spec_before, workspace_module)

        integration.update_active_base_cabinet_shelf_count(4)

        self.assertEqual(
            workspace.preview_read_model.node_count, 8,
            "Expected node_count=8 after shelf_count edit to 4",
        )

    def test_door_count_edit_changes_preview_node_count(self):
        """After door_count edit, PreviewReadModel node_count must
        reflect the new number of scene nodes."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        sg_after = self._make_mock_scene_graph(node_count=10)
        spec_before = self._make_specification(door_count=2)
        eng_service.execute.return_value = self._make_mock_result_from_scene_graph(
            sg_after, door_count=5,
        )
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        workspace.active_engineering_state = self._make_engineering_state(spec_before, workspace_module)

        integration.update_active_base_cabinet_door_count(5)

        self.assertEqual(
            workspace.preview_read_model.node_count, 10,
            "Expected node_count=10 after door_count edit to 5",
        )

    def test_preview_generated_from_active_engineering_state_scene_graph(self):
        """Preview must be generated from ActiveEngineeringState.scene_graph."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        sg = self._make_mock_scene_graph(node_count=5, width=800.0)
        spec_before = self._make_specification()
        eng_service.execute.return_value = self._make_mock_result_from_scene_graph(sg)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        workspace.active_engineering_state = self._make_engineering_state(spec_before, workspace_module)

        integration.update_active_base_cabinet_width(800.0)

        self.assertTrue(workspace.preview_read_model.scene_available)
        self.assertGreater(workspace.preview_read_model.node_count, 0)
        self.assertNotEqual(workspace.preview_read_model.scene_bounds, "")

    def test_preview_not_generated_from_itself(self):
        """PreviewReadModel values must come from the engineering
        result, not from a previously set PreviewReadModel."""
        workspace_module, integration_module, _, read_models = self._import_modules()
        eng_service = Mock()
        sg = self._make_mock_scene_graph(node_count=3, width=800.0, height=900.0, depth=580.0)
        spec_before = self._make_specification()
        eng_service.execute.return_value = self._make_mock_result_from_scene_graph(sg)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        workspace.active_engineering_state = self._make_engineering_state(spec_before, workspace_module)

        # Set a deliberately stale preview
        stale = read_models.PreviewReadModel(
            preview_title="Stale Preview",
            scene_bounds="min=(999,999,999) max=(999,999,999)",
            node_count=999,
            scene_available=False,
        )
        workspace.set_preview_read_model(stale)

        integration.update_active_base_cabinet_width(800.0)

        self.assertNotEqual(
            workspace.preview_read_model.preview_title, "Stale Preview",
            "Preview title must be refreshed, not stale",
        )
        self.assertNotEqual(
            workspace.preview_read_model.scene_bounds, "min=(999,999,999) max=(999,999,999)",
            "Scene bounds must be refreshed, not stale",
        )
        self.assertNotEqual(
            workspace.preview_read_model.node_count, 999,
            "Node count must be refreshed, not stale",
        )

    def test_preview_refresh_after_every_successful_edit(self):
        """Preview must be refreshed after every successful engineering update."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        sg = self._make_mock_scene_graph(node_count=5, width=800.0)
        spec_before = self._make_specification()
        eng_service.execute.return_value = self._make_mock_result_from_scene_graph(sg)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        workspace.active_engineering_state = self._make_engineering_state(spec_before, workspace_module)

        # Capture the workspace's preview model BEFORE the edit
        # (it's the empty default)
        self.assertFalse(workspace.preview_read_model.scene_available)

        integration.update_active_base_cabinet_width(800.0)

        self.assertTrue(
            workspace.preview_read_model.scene_available,
            "Preview must be available (scene_available=True) after edit",
        )

    def test_preview_regeneration_is_deterministic(self):
        """Same inputs must produce the same preview output."""
        workspace_module, integration_module, _, _ = self._import_modules()
        sg = self._make_mock_scene_graph(node_count=5, width=800.0)

        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result_from_scene_graph(sg)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        spec_before = self._make_specification()
        workspace.active_engineering_state = self._make_engineering_state(spec_before, workspace_module)

        integration.update_active_base_cabinet_width(800.0)
        first_bounds = workspace.preview_read_model.scene_bounds
        first_node_count = workspace.preview_read_model.node_count

        # Reset and redo with the same inputs
        eng_service_2 = Mock()
        eng_service_2.execute.return_value = self._make_mock_result_from_scene_graph(sg)
        bindings_2 = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service_2,
        )
        workspace_2 = workspace_module.create_configurator_v2_workspace(service_bindings=bindings_2)
        integration_2 = integration_module.attach_service_integration(workspace_2, bindings_2)
        spec_before_2 = self._make_specification()
        workspace_2.active_engineering_state = self._make_engineering_state(spec_before_2, workspace_module)

        integration_2.update_active_base_cabinet_width(800.0)
        second_bounds = workspace_2.preview_read_model.scene_bounds
        second_node_count = workspace_2.preview_read_model.node_count

        self.assertEqual(first_bounds, second_bounds, "scene_bounds must be deterministic")
        self.assertEqual(first_node_count, second_node_count, "node_count must be deterministic")


if __name__ == "__main__":
    unittest.main()
