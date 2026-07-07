import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


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

    # ── Alpha-UI-4B.2 — Inspector binding to ActiveEngineeringState ──

    def _make_specification(self, width=800.0, height=900.0, depth=600.0, shelf_count=3):
        """Create a specification-like object without importing domain."""
        return types.SimpleNamespace(
            width_mm=width,
            height_mm=height,
            depth_mm=depth,
            shelf_count=shelf_count,
        )

    def _make_engineering_state(self, spec, workspace_module=None):
        """Create an ActiveEngineeringState without importing domain.

        Uses the provided workspace module if given (avoids re-import
        outside the Qt mock context). Falls back to importing fresh
        when no module is provided.
        """
        if workspace_module is not None:
            eng_state_cls = workspace_module.ActiveEngineeringState
        else:
            eng_state_cls = importlib.import_module(
                "ui.configurator_v2.workspace"
            ).ActiveEngineeringState
        return eng_state_cls(
            family="Base Cabinet",
            specification=spec,
            cabinet=None,
            scene_graph=None,
        )

    def test_inspector_reads_width_mm_from_specification(self):
        workspace_module, integration_module, adapters, read_models = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.refresh_inspector(
            {
                "selection_id": "base-cabinet",
                "selection_type": "CABINET",
                "display_name": "Base Cabinet",
                "source_reference": "EngineeringIntegration",
            }
        )

        geometry_labels = workspace.inspector_region.group_field_labels.get("Geometry", [])
        geometry_texts = [getattr(lbl, "_text", "") or "" for lbl in geometry_labels]
        width_rows = [t for t in geometry_texts if "Width" in t]
        self.assertTrue(
            any("800" in t and "mm" in t for t in width_rows),
            f"Expected Width: 800 mm in Geometry fields, got: {geometry_texts}",
        )

    def test_inspector_reads_height_mm_from_specification(self):
        workspace_module, integration_module, adapters, read_models = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(height=900.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.refresh_inspector(
            {
                "selection_id": "base-cabinet",
                "selection_type": "CABINET",
                "display_name": "Base Cabinet",
                "source_reference": "EngineeringIntegration",
            }
        )

        geometry_labels = workspace.inspector_region.group_field_labels.get("Geometry", [])
        geometry_texts = [getattr(lbl, "_text", "") or "" for lbl in geometry_labels]
        height_rows = [t for t in geometry_texts if "Height" in t]
        self.assertTrue(
            any("900" in t and "mm" in t for t in height_rows),
            f"Expected Height: 900 mm in Geometry fields, got: {geometry_texts}",
        )

    def test_inspector_reads_depth_mm_from_specification(self):
        workspace_module, integration_module, adapters, read_models = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(depth=600.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.refresh_inspector(
            {
                "selection_id": "base-cabinet",
                "selection_type": "CABINET",
                "display_name": "Base Cabinet",
                "source_reference": "EngineeringIntegration",
            }
        )

        geometry_labels = workspace.inspector_region.group_field_labels.get("Geometry", [])
        geometry_texts = [getattr(lbl, "_text", "") or "" for lbl in geometry_labels]
        depth_rows = [t for t in geometry_texts if "Depth" in t]
        self.assertTrue(
            any("600" in t and "mm" in t for t in depth_rows),
            f"Expected Depth: 600 mm in Geometry fields, got: {geometry_texts}",
        )

    def test_inspector_not_from_preview_read_model(self):
        """Inspector must NOT read dimensions from PreviewReadModel."""
        workspace_module, integration_module, adapters, read_models = self._import_modules()
        workspace = workspace_module.create_configurator_v2_workspace()
        preview_rm = read_models.PreviewReadModel(
            preview_title="Test Cabinet",
            preview_state="Ready",
            scene_available=True,
            node_count=10,
            scene_bounds="800 x 900 x 600",
        )
        workspace.set_preview_read_model(preview_rm)
        workspace.set_inspector_read_model(
            read_models.InspectorReadModel(
                selection_id="cabinet-1",
                selection_type="CABINET",
                display_name="Cabinet",
            )
        )

        geometry_labels = workspace.inspector_region.group_field_labels.get("Geometry", [])
        render_rows = workspace.inspector_region.render_rows

        self.assertFalse(
            any("Width" in r for r in render_rows),
            f"Inspector should not show Width from PreviewReadModel, got: {render_rows}",
        )
        self.assertFalse(
            any("Height" in r for r in render_rows),
            "Inspector should not show Height from PreviewReadModel",
        )
        self.assertFalse(
            any("Depth" in r for r in render_rows),
            "Inspector should not show Depth from PreviewReadModel",
        )

    def test_inspector_preserves_existing_fields_when_enriched(self):
        """Specification enrichment must preserve existing fields and sections."""
        workspace_module, integration_module, adapters, read_models = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=900.0, depth=600.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.refresh_inspector(
            {
                "selection_id": "cabinet-1",
                "selection_type": "CABINET",
                "display_name": "Cabinet",
                "source_reference": "ProjectTreeRegion",
                "fields": [
                    {"name": "family", "label": "Family", "value": "Base Cabinet", "group": "Identity"},
                    {"name": "material", "label": "Material", "value": "Birch Plywood", "group": "Materials"},
                ],
                "warnings": ["Check door hinge"],
                "stale": False,
            }
        )

        render_rows = workspace.inspector_region.render_rows
        identity_labels = workspace.inspector_region.group_field_labels.get("Identity", [])
        identity_texts = [getattr(lbl, "_text", "") or "" for lbl in identity_labels]
        materials_labels = workspace.inspector_region.group_field_labels.get("Materials", [])
        materials_texts = [getattr(lbl, "_text", "") or "" for lbl in materials_labels]

        # Original fields preserved
        self.assertTrue(
            any("Family: Base Cabinet" in t for t in identity_texts),
            f"Existing Identity fields lost, got: {identity_texts}",
        )
        self.assertTrue(
            any("Material: Birch Plywood" in t for t in materials_texts),
            f"Existing Materials fields lost, got: {materials_texts}",
        )
        # Specification fields present
        geometry_labels = workspace.inspector_region.group_field_labels.get("Geometry", [])
        geometry_texts = [getattr(lbl, "_text", "") or "" for lbl in geometry_labels]
        self.assertTrue(
            any("Width: 800" in t for t in geometry_texts),
            f"Specification Width field missing, got: {geometry_texts}",
        )
        self.assertTrue(
            any("Height: 900" in t for t in geometry_texts),
            "Specification Height field missing",
        )
        self.assertTrue(
            any("Depth: 600" in t for t in geometry_texts),
            "Specification Depth field missing",
        )
        # Warnings preserved
        self.assertTrue(
            any("Warnings: Check door hinge" in r for r in render_rows),
            "Existing warnings lost",
        )

    def test_editable_dimension_fields_render_as_input_controls(self):
        """Editable dimension fields must render as input-capable widgets."""
        workspace_module, integration_module, adapters, read_models = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=900.0, depth=600.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.refresh_inspector(
            {
                "selection_id": "cabinet-1",
                "selection_type": "CABINET",
                "display_name": "Cabinet",
                "source_reference": "ProjectTreeRegion",
                "fields": [
                    {"name": "family", "label": "Family", "value": "Base Cabinet", "group": "Identity"},
                ],
            }
        )

        self.assertIn("width_mm", workspace.inspector_region.editable_field_inputs)
        self.assertIn("height_mm", workspace.inspector_region.editable_field_inputs)
        self.assertIn("depth_mm", workspace.inspector_region.editable_field_inputs)
        self.assertNotIn("family", workspace.inspector_region.editable_field_inputs)
        self.assertEqual(
            workspace.inspector_region.editable_field_inputs["width_mm"].text(),
            "800.0",
        )

    def test_width_edit_calls_update_active_base_cabinet_width(self):
        """Committing width from the inspector must call the width update method."""
        workspace_module, integration_module, _, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        integration.update_active_base_cabinet_width = Mock(return_value=workspace.preview_read_model)

        spec = self._make_specification(width=800.0, height=900.0, depth=600.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="base-cabinet",
                display_name="Base Cabinet",
                source_region="EngineeringIntegration",
            )
        )

        editor = workspace.inspector_region.editable_field_inputs["width_mm"]
        editor.setText("900.0")
        editor.editingFinished.emit()

        integration.update_active_base_cabinet_width.assert_called_once_with(900.0)

    def test_height_edit_calls_update_active_base_cabinet_height(self):
        """Committing height from the inspector must call the height update method."""
        workspace_module, integration_module, _, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        integration.update_active_base_cabinet_height = Mock(return_value=workspace.preview_read_model)

        spec = self._make_specification(width=800.0, height=900.0, depth=600.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="base-cabinet",
                display_name="Base Cabinet",
                source_region="EngineeringIntegration",
            )
        )

        editor = workspace.inspector_region.editable_field_inputs["height_mm"]
        editor.setText("950.0")
        editor.editingFinished.emit()

        integration.update_active_base_cabinet_height.assert_called_once_with(950.0)

    def test_depth_edit_calls_update_active_base_cabinet_depth(self):
        """Committing depth from the inspector must call the depth update method."""
        workspace_module, integration_module, _, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        integration.update_active_base_cabinet_depth = Mock(return_value=workspace.preview_read_model)

        spec = self._make_specification(width=800.0, height=900.0, depth=600.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="base-cabinet",
                display_name="Base Cabinet",
                source_region="EngineeringIntegration",
            )
        )

        editor = workspace.inspector_region.editable_field_inputs["depth_mm"]
        editor.setText("650.0")
        editor.editingFinished.emit()

        integration.update_active_base_cabinet_depth.assert_called_once_with(650.0)

    def test_non_editable_fields_do_not_trigger_edits(self):
        """Non-editable inspector fields must remain passive."""
        workspace_module, integration_module, _, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        integration.update_active_base_cabinet_width = Mock(return_value=workspace.preview_read_model)
        integration.update_active_base_cabinet_height = Mock(return_value=workspace.preview_read_model)
        integration.update_active_base_cabinet_depth = Mock(return_value=workspace.preview_read_model)

        spec = self._make_specification(width=800.0, height=900.0, depth=600.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.refresh_inspector(
            {
                "selection_id": "cabinet-1",
                "selection_type": "CABINET",
                "display_name": "Cabinet",
                "source_reference": "ProjectTreeRegion",
                "fields": [
                    {"name": "family", "label": "Family", "value": "Base Cabinet", "group": "Identity"},
                ],
            }
        )

        self.assertNotIn("family", workspace.inspector_region.editable_field_inputs)
        self.assertFalse(integration.update_active_base_cabinet_width.called)
        self.assertFalse(integration.update_active_base_cabinet_height.called)
        self.assertFalse(integration.update_active_base_cabinet_depth.called)

    def test_specification_fields_are_editable(self):
        """Specification dimension fields must be marked editable=True."""
        workspace_module, _, adapters_mod, _ = self._import_modules()
        spec = self._make_specification(width=800.0, height=900.0, depth=600.0)

        enriched = adapters_mod.enrich_inspector_source_with_specification(
            {"selection_id": "cabinet-1"},
            self._make_engineering_state(spec, workspace_module),
        )

        fields = enriched.get("fields", [])
        width_fields = [f for f in fields if f.get("name") == "width_mm"]
        height_fields = [f for f in fields if f.get("name") == "height_mm"]
        depth_fields = [f for f in fields if f.get("name") == "depth_mm"]

        self.assertEqual(len(width_fields), 1, "Expected one width_mm field")
        self.assertEqual(len(height_fields), 1, "Expected one height_mm field")
        self.assertEqual(len(depth_fields), 1, "Expected one depth_mm field")

        self.assertTrue(width_fields[0].get("editable"), "width_mm must be editable=True")
        self.assertTrue(height_fields[0].get("editable"), "height_mm must be editable=True")
        self.assertTrue(depth_fields[0].get("editable"), "depth_mm must be editable=True")
        self.assertEqual(width_fields[0].get("unit"), "mm", "width_mm unit must be mm")
        self.assertEqual(height_fields[0].get("unit"), "mm", "height_mm unit must be mm")
        self.assertEqual(depth_fields[0].get("unit"), "mm", "depth_mm unit must be mm")

    def test_no_forbidden_imports_in_specification_enrichment_path(self):
        """Domain modules must not be imported via the specification enrichment path."""
        forbidden_modules = (
            "domain.base_cabinet_engineering_entry",
            "domain.base_cabinet_specification",
            "manufacturing.factory_release_package",
            "manufacturing.factory_decision_projection",
            "manufacturing.manufacturing_production_package",
            "commercial_outputs.commercial_package_report",
            "cost_intelligence.quotation_document",
        )
        for module_name in forbidden_modules:
            sys.modules.pop(module_name, None)

        workspace_module, _, adapters_mod, _ = self._import_modules()

        spec = self._make_specification(width=800.0)
        eng_state = self._make_engineering_state(spec, workspace_module)

        # Call the enrichment function directly
        result = adapters_mod.enrich_inspector_source_with_specification(
            {"selection_id": "cabinet-1"},
            eng_state,
        )

        self.assertIsNotNone(result)
        self.assertIn("fields", result)

        for module_name in forbidden_modules:
            self.assertNotIn(
                module_name,
                sys.modules,
                f"Forbidden module imported: {module_name}",
            )

    def test_specification_not_mutated_by_enrichment(self):
        """The specification must not be mutated by the enrichment path."""
        workspace_module, _, adapters_mod, _ = self._import_modules()
        spec = self._make_specification(width=800.0, height=900.0, depth=600.0)
        eng_state = self._make_engineering_state(spec, workspace_module)

        expected_width = spec.width_mm
        expected_height = spec.height_mm
        expected_depth = spec.depth_mm

        adapters_mod.enrich_inspector_source_with_specification(
            {"selection_id": "cabinet-1"},
            eng_state,
        )

        self.assertEqual(spec.width_mm, expected_width, "width_mm was mutated")
        self.assertEqual(spec.height_mm, expected_height, "height_mm was mutated")
        self.assertEqual(spec.depth_mm, expected_depth, "depth_mm was mutated")

    def test_no_active_state_returns_empty_inspector(self):
        """When no active engineering state exists, inspector must remain empty."""
        workspace_module, integration_module, adapters, read_models = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        # No active_engineering_state set — default is empty ActiveEngineeringState with no spec
        workspace.active_engineering_state = workspace_module.ActiveEngineeringState()

        result = integration.refresh_inspector(
            {
                "selection_id": "cabinet-1",
                "selection_type": "CABINET",
                "display_name": "Cabinet",
            }
        )

        geometry_labels = workspace.inspector_region.group_field_labels.get("Geometry", [])
        geometry_texts = [getattr(lbl, "_text", "") or "" for lbl in geometry_labels]
        self.assertFalse(
            any("Width" in t for t in geometry_texts),
            "No Width should appear without specification",
        )
        self.assertFalse(
            any("Height" in t for t in geometry_texts),
            "No Height should appear without specification",
        )
        self.assertEqual(result.selection_id, "cabinet-1")

    # ── Alpha-UI-4B.3 — Live height and depth editing ──────────────

    def _make_mock_result(self, width=800.0, height=900.0, depth=600.0, shelf_count=3):
        """Create a mock engineering service result with a simple scene."""
        spec = types.SimpleNamespace(
            width_mm=width, height_mm=height, depth_mm=depth,
            shelf_count=shelf_count,
        )
        scene = types.SimpleNamespace()
        cabinet = types.SimpleNamespace(scene_graph=scene)
        result = Mock()
        result.data = {"cabinet": cabinet, "specification": spec, "metadata": {}}
        result.errors = ()
        result.diagnostics = ()
        return result

    def test_height_edit_calls_engineering_service(self):
        """Height change must call engineering_application_service.execute."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(height=720.0)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=720.0, depth=580.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.update_active_base_cabinet_height(750.0)

        eng_service.execute.assert_called_once()
        call_args = eng_service.execute.call_args
        self.assertIn("specification", call_args.kwargs)
        executed_spec = call_args.kwargs["specification"]
        self.assertEqual(executed_spec.height_mm, 750.0)

    def test_depth_edit_calls_engineering_service(self):
        """Depth change must call engineering_application_service.execute."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(depth=580.0)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=720.0, depth=580.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.update_active_base_cabinet_depth(600.0)

        eng_service.execute.assert_called_once()
        call_args = eng_service.execute.call_args
        self.assertIn("specification", call_args.kwargs)
        executed_spec = call_args.kwargs["specification"]
        self.assertEqual(executed_spec.depth_mm, 600.0)

    def test_width_edit_still_works_after_refactor(self):
        """Width editing must continue to work after the helper refactor."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(width=600.0)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=720.0, depth=580.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.update_active_base_cabinet_width(600.0)

        eng_service.execute.assert_called_once()
        call_args = eng_service.execute.call_args
        executed_spec = call_args.kwargs["specification"]
        self.assertEqual(executed_spec.width_mm, 600.0)

    def test_height_edit_preserves_width_and_depth(self):
        """Height must preserve width/depth of the copied specification."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(width=800.0, height=750.0, depth=580.0)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=720.0, depth=580.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.update_active_base_cabinet_height(750.0)

        call_args = eng_service.execute.call_args
        executed_spec = call_args.kwargs["specification"]
        self.assertEqual(executed_spec.width_mm, 800.0, "width_mm was changed by height edit")
        self.assertEqual(executed_spec.depth_mm, 580.0, "depth_mm was changed by height edit")
        self.assertEqual(executed_spec.height_mm, 750.0, "height_mm was not updated")

    def test_depth_edit_preserves_width_and_height(self):
        """Depth must preserve width/height of the copied specification."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(width=800.0, height=720.0, depth=600.0)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=720.0, depth=580.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.update_active_base_cabinet_depth(600.0)

        call_args = eng_service.execute.call_args
        executed_spec = call_args.kwargs["specification"]
        self.assertEqual(executed_spec.width_mm, 800.0, "width_mm was changed by depth edit")
        self.assertEqual(executed_spec.height_mm, 720.0, "height_mm was changed by depth edit")
        self.assertEqual(executed_spec.depth_mm, 600.0, "depth_mm was not updated")

    def test_invalid_dimension_field_rejected(self):
        """An invalid field name must be rejected safely."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=720.0, depth=580.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        result = integration._update_active_base_cabinet_dimension("length_mm", 500.0)

        eng_service.execute.assert_not_called()
        self.assertIs(result, workspace.preview_read_model)

    def test_dimension_edit_does_not_mutate_original_specification(self):
        """The original specification must not be mutated by the edit."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(width=600.0, height=720.0, depth=580.0)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=720.0, depth=580.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.update_active_base_cabinet_width(600.0)

        self.assertEqual(spec.width_mm, 800.0, "Original specification width was mutated")
        self.assertEqual(spec.height_mm, 720.0, "Original specification height was mutated")
        self.assertEqual(spec.depth_mm, 580.0, "Original specification depth was mutated")

    def test_stale_flags_set_on_dimension_edit(self):
        """Manufacturing/cost/commercial must be stale after dimension edit."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(width=800.0, height=900.0, depth=600.0)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=720.0, depth=580.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.update_active_base_cabinet_height(900.0)

        state = workspace.active_engineering_state
        self.assertFalse(state.engineering_dirty, "engineering_dirty should be False")
        self.assertTrue(state.manufacturing_stale, "manufacturing_stale should be True")
        self.assertTrue(state.cost_stale, "cost_stale should be True")
        self.assertTrue(state.commercial_stale, "commercial_stale should be True")

    def test_preview_not_source_of_truth_for_dimension_edit(self):
        """PreviewReadModel values must not be the source of truth for dimension edits."""
        workspace_module, integration_module, _, read_models = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(width=800.0, height=900.0, depth=600.0)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=720.0, depth=580.0)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        # Set a preview with deliberately wrong dimensions
        bad_preview = read_models.PreviewReadModel(
            preview_title="Stale Preview",
            scene_bounds="999 x 999 x 999",
        )
        workspace.set_preview_read_model(bad_preview)

        integration.update_active_base_cabinet_height(900.0)

        state_spec = workspace.active_engineering_state.specification
        self.assertEqual(state_spec.height_mm, 900.0,
                         "Spec height should come from engineering result, not preview")
        self.assertNotEqual(state_spec.height_mm, 999.0,
                            "Spec height must not come from PreviewReadModel bounds")

    def test_no_forbidden_imports_in_dimension_edit_path(self):
        """Domain modules must not be imported via the dimension edit path."""
        forbidden_modules = (
            "domain.base_cabinet_engineering_entry",
            "domain.base_cabinet_specification",
            "manufacturing.factory_release_package",
            "manufacturing.factory_decision_projection",
            "manufacturing.manufacturing_production_package",
            "commercial_outputs.commercial_package_report",
            "cost_intelligence.quotation_document",
        )
        for module_name in forbidden_modules:
            sys.modules.pop(module_name, None)

        workspace_module, _, _, _ = self._import_modules()

        for module_name in forbidden_modules:
            self.assertNotIn(module_name, sys.modules,
                             f"Forbidden module imported via dimension edit path: {module_name}")

    # ── Alpha-UI-5B — Live shelf count editing ────────────────────

    def test_shelf_count_appears_in_inspector(self):
        """shelf_count value must appear in the Inspector from specification."""
        workspace_module, integration_module, _, read_models = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(shelf_count=4)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.refresh_inspector(
            {
                "selection_id": "base-cabinet",
                "selection_type": "CABINET",
                "display_name": "Base Cabinet",
            }
        )

        config_labels = workspace.inspector_region.group_field_labels.get("Configuration", [])
        config_texts = [getattr(lbl, "_text", "") or "" for lbl in config_labels]
        self.assertTrue(
            any("Shelf Count: 4" in t for t in config_texts),
            f"Expected 'Shelf Count: 4' in Configuration fields, got: {config_texts}",
        )

    def test_shelf_count_field_is_editable(self):
        """shelf_count must be marked editable=True in the inspector enrichment."""
        workspace_module, _, adapters_mod, _ = self._import_modules()
        spec = self._make_specification(shelf_count=4)

        enriched = adapters_mod.enrich_inspector_source_with_specification(
            {"selection_id": "cabinet-1"},
            self._make_engineering_state(spec, workspace_module),
        )

        fields = enriched.get("fields", [])
        shelf_fields = [f for f in fields if f.get("name") == "shelf_count"]
        self.assertEqual(len(shelf_fields), 1, "Expected one shelf_count field")
        self.assertTrue(shelf_fields[0].get("editable"), "shelf_count must be editable=True")
        self.assertEqual(shelf_fields[0].get("group"), "Configuration",
                         "shelf_count group must be Configuration")
        self.assertEqual(shelf_fields[0].get("unit"), "",
                         "shelf_count unit must be empty string")

    def test_shelf_count_renders_as_editable_input(self):
        """shelf_count must render as an input-capable control in the inspector."""
        workspace_module, integration_module, _, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        integration.update_active_base_cabinet_width = Mock(return_value=workspace.preview_read_model)
        integration.update_active_base_cabinet_height = Mock(return_value=workspace.preview_read_model)
        integration.update_active_base_cabinet_depth = Mock(return_value=workspace.preview_read_model)
        integration.update_active_base_cabinet_shelf_count = Mock(return_value=workspace.preview_read_model)

        spec = self._make_specification(width=800.0, height=900.0, depth=600.0, shelf_count=3)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="base-cabinet",
                display_name="Base Cabinet",
                source_region="EngineeringIntegration",
            )
        )

        self.assertIn("shelf_count", workspace.inspector_region.editable_field_inputs)
        self.assertEqual(
            workspace.inspector_region.editable_field_inputs["shelf_count"].text(),
            "3",
        )

    def test_shelf_count_commit_calls_update_method(self):
        """Committing shelf_count from the inspector must call update method."""
        workspace_module, integration_module, _, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        integration.update_active_base_cabinet_shelf_count = Mock(
            return_value=workspace.preview_read_model
        )

        spec = self._make_specification(width=800.0, height=900.0, depth=600.0, shelf_count=3)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="base-cabinet",
                display_name="Base Cabinet",
                source_region="EngineeringIntegration",
            )
        )

        editor = workspace.inspector_region.editable_field_inputs["shelf_count"]
        editor.setText("5")
        editor.editingFinished.emit()

        integration.update_active_base_cabinet_shelf_count.assert_called_once_with(5)

    def test_shelf_count_edit_calls_engineering_service(self):
        """shelf_count edit must call engineering_application_service.execute."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(shelf_count=5)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=900.0, depth=600.0, shelf_count=3)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.update_active_base_cabinet_shelf_count(5)

        eng_service.execute.assert_called_once()
        call_args = eng_service.execute.call_args
        self.assertIn("specification", call_args.kwargs)
        executed_spec = call_args.kwargs["specification"]
        self.assertEqual(executed_spec.shelf_count, 5)

    def test_shelf_count_edit_preserves_dimensions(self):
        """shelf_count edit must preserve width/height/depth."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(
            width=800.0, height=900.0, depth=600.0, shelf_count=5,
        )
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(width=800.0, height=900.0, depth=600.0, shelf_count=3)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.update_active_base_cabinet_shelf_count(5)

        call_args = eng_service.execute.call_args
        executed_spec = call_args.kwargs["specification"]
        self.assertEqual(executed_spec.width_mm, 800.0, "width_mm changed by shelf_count edit")
        self.assertEqual(executed_spec.height_mm, 900.0, "height_mm changed by shelf_count edit")
        self.assertEqual(executed_spec.depth_mm, 600.0, "depth_mm changed by shelf_count edit")
        self.assertEqual(executed_spec.shelf_count, 5, "shelf_count not updated")

    def test_invalid_shelf_count_rejected(self):
        """Negative integer must be rejected for shelf_count."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(shelf_count=3)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        result = integration.update_active_base_cabinet_shelf_count(-1)

        eng_service.execute.assert_not_called()
        self.assertIs(result, workspace.preview_read_model)

    def test_shelf_count_edit_does_not_mutate_original_specification(self):
        """Original specification must not be mutated by shelf_count edit."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(shelf_count=5)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(shelf_count=3)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.update_active_base_cabinet_shelf_count(5)

        self.assertEqual(spec.shelf_count, 3, "Original specification shelf_count was mutated")

    def test_stale_flags_set_on_shelf_count_edit(self):
        """Manufacturing/cost/commercial must be stale after shelf_count edit."""
        workspace_module, integration_module, _, _ = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(shelf_count=5)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(shelf_count=3)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        integration.update_active_base_cabinet_shelf_count(5)

        state = workspace.active_engineering_state
        self.assertFalse(state.engineering_dirty, "engineering_dirty should be False")
        self.assertTrue(state.manufacturing_stale, "manufacturing_stale should be True")
        self.assertTrue(state.cost_stale, "cost_stale should be True")
        self.assertTrue(state.commercial_stale, "commercial_stale should be True")

    def test_preview_not_source_of_truth_for_shelf_count(self):
        """PreviewReadModel must not be the source of truth for shelf_count."""
        workspace_module, integration_module, _, read_models = self._import_modules()
        eng_service = Mock()
        eng_service.execute.return_value = self._make_mock_result(shelf_count=5)
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            engineering_application_service=eng_service,
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)

        spec = self._make_specification(shelf_count=3)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        bad_preview = read_models.PreviewReadModel(
            preview_title="Stale",
        )
        workspace.set_preview_read_model(bad_preview)

        integration.update_active_base_cabinet_shelf_count(5)

        state_spec = workspace.active_engineering_state.specification
        self.assertEqual(state_spec.shelf_count, 5,
                         "Spec shelf_count should come from engineering result, not preview")

    def test_non_editable_config_fields_remain_read_only(self):
        """Non-editable fields (e.g. door_count) must remain passive.

        Without specification enrichment, metadata-derived fields have
        editable=False and must NOT appear as input controls.
        """
        workspace_module, integration_module, _, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        integration.update_active_base_cabinet_shelf_count = Mock(
            return_value=workspace.preview_read_model
        )

        # No active engineering state — metadata-only path has editable=False
        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="base-cabinet",
                display_name="Base Cabinet",
                source_region="EngineeringIntegration",
                metadata={
                    "width_mm": "800",
                    "height_mm": "900",
                    "depth_mm": "600",
                    "shelf_count": "3",
                    "door_count": "2",
                },
            )
        )

        editable_inputs = workspace.inspector_region.editable_field_inputs
        # Without specification enrichment, no fields should be editable
        # because metadata-derived fields have editable=False
        self.assertEqual(
            len(editable_inputs), 0,
            f"No fields should be editable without specification enrichment, "
            f"got: {list(editable_inputs.keys())}",
        )
        self.assertFalse(
            integration.update_active_base_cabinet_shelf_count.called,
        )

    def test_shelf_count_is_editable_only_with_specification(self):
        """shelf_count becomes editable only when specification enrichment is active."""
        workspace_module, integration_module, _, _ = self._import_modules()
        bindings = workspace_module.ConfiguratorV2ServiceBindings(
            project_application_service=Mock(),
            engineering_application_service=Mock(),
            manufacturing_application_service=Mock(),
        )
        workspace = workspace_module.create_configurator_v2_workspace(service_bindings=bindings)
        integration = integration_module.attach_service_integration(workspace, bindings)
        integration.update_active_base_cabinet_shelf_count = Mock(
            return_value=workspace.preview_read_model
        )

        spec = self._make_specification(shelf_count=3)
        workspace.active_engineering_state = self._make_engineering_state(spec, workspace_module)

        workspace.set_selection(
            workspace_module.ConfiguratorSelection(
                selection_type="CABINET",
                selection_id="base-cabinet",
                display_name="Base Cabinet",
                source_region="EngineeringIntegration",
            )
        )

        self.assertIn("shelf_count", workspace.inspector_region.editable_field_inputs)
        self.assertEqual(
            workspace.inspector_region.editable_field_inputs["shelf_count"].text(),
            "3",
        )

    def test_no_forbidden_imports_in_shelf_count_path(self):
        """No domain modules imported via shelf_count editing path."""
        forbidden_modules = (
            "domain.base_cabinet_engineering_entry",
            "domain.base_cabinet_specification",
            "manufacturing.factory_release_package",
            "manufacturing.factory_decision_projection",
            "manufacturing.manufacturing_production_package",
            "commercial_outputs.commercial_package_report",
            "cost_intelligence.quotation_document",
        )
        for module_name in forbidden_modules:
            sys.modules.pop(module_name, None)

        workspace_module, _, _, _ = self._import_modules()

        for module_name in forbidden_modules:
            self.assertNotIn(
                module_name, sys.modules,
                f"Forbidden module imported via shelf_count path: {module_name}",
            )


if __name__ == "__main__":
    unittest.main()
