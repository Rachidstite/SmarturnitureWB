# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Inspector Presentation Awareness Contract Tests
#
# Verifies:
# - inspector reads neutral state from component with no presentation
# - inspector reads selected state and visual contract
# - inspector reads warning/error dominant visual intent
# - inspector exposes visual severity consistently
# - descriptor pairs are deterministic
# - missing presentation data falls back safely
# - existing component metadata preserved
# - no mutation of input components
# - no domain/manufacturing/cost/Qt imports
# - no engine/workflow/event-bus naming
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest
from unittest.mock import patch


def _fake_qt():
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


class TestInspectorPresentationAwarenessContract(unittest.TestCase):
    """Verify inspector presentation awareness integration."""

    @classmethod
    def _import_modules(cls):
        for key in list(sys.modules):
            if key.startswith("ui.configurator_v2"):
                del sys.modules[key]

        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt()}):
            ws = __import__("ui.configurator_v2.workspace", fromlist=["ConfiguratorV2Workspace", "create_configurator_v2_workspace"])
            interactive = __import__("ui.configurator_v2.interactive_components", fromlist=["InteractiveVisualComponent", "build_interactive_visual_components"])
            vc = __import__("ui.configurator_v2.visual_components", fromlist=["DoorVisualComponent", "PanelVisualComponent"])
            read_models = __import__("ui.configurator_v2.read_models", fromlist=["InspectorFieldReadModel", "InspectorReadModel"])
            adapters = __import__("ui.configurator_v2.projection_adapters", fromlist=["build_inspector_read_model"])
            sync = __import__("ui.configurator_v2.presentation_synchronization", fromlist=["synchronize_presentation"])
            ps = __import__("ui.configurator_v2.presentation_state", fromlist=["FurniturePresentationState"])
            pvc = __import__("ui.configurator_v2.presentation_visual_contract", fromlist=["PresentationVisualContract", "OUTLINE_SELECTED", "OUTLINE_ERROR"])
        return ws, interactive, vc, read_models, adapters, sync, ps, pvc

    @classmethod
    def _make_selection(cls, ws_mod, selection_id="c1", selection_type="DOOR", display_name="Door"):
        return ws_mod.ConfiguratorSelection(
            selection_type=selection_type,
            selection_id=selection_id,
            display_name=display_name,
            source_region="test",
        )

    # ── Rule 1: neutral state → no presentation fields ───────────

    def test_neutral_component_has_no_presentation_fields(self):
        """Interactive component with no presentation data produces no extra fields."""
        ws, interactive, vc, _, _, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)

        # Select with no flag sets — neutral
        workspace.synchronize_preview_interactive_components(interactives)
        synced = workspace.preview_region.interactive_components[0]
        sel = self._make_selection(ws, selection_id="d1")

        workspace.set_presentation_aware_inspector(sel, synced)
        inspector = workspace.inspector_read_model

        # Should have no presentation fields
        presentation_fields = [f for f in inspector.fields if f.group == "Presentation"]
        self.assertEqual(len(presentation_fields), 0)

    def test_workspace_stores_presentation_fields_when_present(self):
        """Interactive component with presentation data produces Presentation fields."""
        ws, interactive, vc, _, _, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives, selected_ids=frozenset({"d1"})
        )
        synced = workspace.preview_region.interactive_components[0]
        sel = self._make_selection(ws, selection_id="d1")

        workspace.set_presentation_aware_inspector(sel, synced)
        inspector = workspace.inspector_read_model

        presentation_fields = [f for f in inspector.fields if f.group == "Presentation"]
        self.assertGreater(len(presentation_fields), 0)

    # ── Rule 2: selected state and visual contract ───────────────

    def test_selected_state_appears_in_inspector(self):
        """Selected component's presentation state appears in inspector."""
        ws, interactive, vc, read_models, _, _, _, pvc = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives, selected_ids=frozenset({"d1"})
        )
        synced = workspace.preview_region.interactive_components[0]
        sel = self._make_selection(ws, selection_id="d1")

        workspace.set_presentation_aware_inspector(sel, synced)
        inspector = workspace.inspector_read_model

        fields = {f.name: f.value for f in inspector.fields}
        # Should have presentation fields
        self.assertIn("presentation_component_id", fields)
        self.assertIn("presentation_flags", fields)
        self.assertEqual(fields.get("presentation_dominant"), "selected")
        # Visual contract should show SELECTED outline
        self.assertEqual(fields.get("vc_outline"), pvc.OUTLINE_SELECTED)

    # ── Rule 3: warning/error dominant visual intent ─────────────

    def test_error_dominant_appears_in_inspector(self):
        """Error component shows error dominant and CRITICAL emphasis."""
        ws, interactive, vc, _, _, _, _, pvc = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.PanelVisualComponent(id="p1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives, error_ids=frozenset({"p1"})
        )
        synced = workspace.preview_region.interactive_components[0]
        sel = self._make_selection(ws, selection_id="p1", selection_type="PANEL")

        workspace.set_presentation_aware_inspector(sel, synced)
        fields = {f.name: f.value for f in workspace.inspector_read_model.fields}

        self.assertEqual(fields.get("presentation_dominant"), "error")
        self.assertEqual(fields.get("presentation_severity"), "50")
        self.assertEqual(fields.get("vc_emphasis"), pvc.EMPHASIS_CRITICAL)
        self.assertEqual(fields.get("vc_outline"), pvc.OUTLINE_ERROR)

    def test_warning_dominant_appears_in_inspector(self):
        """Warning component shows warning dominant and HIGH emphasis."""
        ws, interactive, vc, _, _, _, _, pvc = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.PanelVisualComponent(id="p1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives, warning_ids=frozenset({"p1"})
        )
        synced = workspace.preview_region.interactive_components[0]
        sel = self._make_selection(ws, selection_id="p1", selection_type="PANEL")

        workspace.set_presentation_aware_inspector(sel, synced)
        fields = {f.name: f.value for f in workspace.inspector_read_model.fields}

        self.assertEqual(fields.get("presentation_dominant"), "warning")
        self.assertEqual(fields.get("presentation_severity"), "40")
        self.assertEqual(fields.get("vc_emphasis"), pvc.EMPHASIS_HIGH)
        self.assertEqual(fields.get("vc_outline"), pvc.OUTLINE_WARNING)

    # ── Rule 4: visual severity consistency ──────────────────────

    def test_visual_severity_consistent(self):
        """Visual severity is consistent between state and contract fields."""
        ws, interactive, vc, _, _, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.PanelVisualComponent(id="p1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives,
            warning_ids=frozenset({"p1"}),
            error_ids=frozenset({"p1"}),
        )
        synced = workspace.preview_region.interactive_components[0]
        sel = self._make_selection(ws, selection_id="p1", selection_type="PANEL")

        workspace.set_presentation_aware_inspector(sel, synced)
        fields = {f.name: f.value for f in workspace.inspector_read_model.fields}

        # Severity should be 50 (error wins over warning)
        self.assertEqual(fields.get("presentation_severity"), "50")
        self.assertEqual(fields.get("vc_priority"), "50")

    # ── Rule 5: deterministic ────────────────────────────────────

    def test_inspector_fields_deterministic(self):
        """Same input produces same inspector fields."""
        ws, interactive, vc, _, _, _, _, _ = self._import_modules()

        def _get_fields():
            w = ws.create_configurator_v2_workspace()
            components = (vc.DoorVisualComponent(id="d1"),)
            interactives = interactive.build_interactive_visual_components(components)
            w.synchronize_preview_interactive_components(
                interactives, selected_ids=frozenset({"d1"})
            )
            synced = w.preview_region.interactive_components[0]
            sel = self._make_selection(ws, selection_id="d1")
            w.set_presentation_aware_inspector(sel, synced)
            return {f.name: f.value for f in w.inspector_read_model.fields}

        fields1 = _get_fields()
        fields2 = _get_fields()
        self.assertEqual(fields1, fields2)

    # ── Rule 6: missing presentation falls back safely ───────────

    def test_no_interactive_component_returns_base(self):
        """set_presentation_aware_inspector with None interactive returns base inspector."""
        ws, _, _, _, _, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        sel = self._make_selection(ws, selection_id="c1")
        workspace.set_presentation_aware_inspector(sel, interactive_component=None)

        inspector = workspace.inspector_read_model
        # No Presentation group fields
        presentation_fields = [f for f in inspector.fields if f.group == "Presentation"]
        self.assertEqual(len(presentation_fields), 0)
        # Base read model attributes still present
        self.assertEqual(inspector.selection_id, "c1")

    def test_component_without_presentation_returns_base(self):
        """Interactive component without presentation data returns base inspector."""
        ws, interactive, vc, _, _, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        # Build component with no presentation attached
        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.set_preview_interactive_components(interactives)
        neutral_ic = workspace.preview_region.interactive_components[0]
        sel = self._make_selection(ws, selection_id="d1")

        workspace.set_presentation_aware_inspector(sel, neutral_ic)
        presentation_fields = [f for f in workspace.inspector_read_model.fields if f.group == "Presentation"]
        self.assertEqual(len(presentation_fields), 0)

    # ── Rule 7: existing metadata preserved ──────────────────────

    def test_existing_metadata_preserved(self):
        """Base inspector metadata remains unchanged after adding presentation fields."""
        ws, interactive, vc, _, _, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives, selected_ids=frozenset({"d1"})
        )
        synced = workspace.preview_region.interactive_components[0]
        sel = self._make_selection(ws, selection_id="d1", selection_type="DOOR", display_name="Door")

        workspace.set_presentation_aware_inspector(sel, synced)
        inspector = workspace.inspector_read_model

        self.assertEqual(inspector.selection_id, "d1")
        self.assertEqual(inspector.selection_type, "DOOR")
        self.assertEqual(inspector.display_name, "Door")

    # ── Rule 8: no input mutation ────────────────────────────────

    def test_no_mutation_of_input(self):
        """set_presentation_aware_inspector does not mutate input components."""
        ws, interactive, vc, _, _, _, ps, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives, selected_ids=frozenset({"d1"})
        )
        synced = workspace.preview_region.interactive_components[0]
        orig_presentation = synced.interaction.presentation
        sel = self._make_selection(ws, selection_id="d1")

        workspace.set_presentation_aware_inspector(sel, synced)

        # Original component unchanged
        self.assertIs(synced.interaction.presentation, orig_presentation)
        self.assertTrue(synced.interaction.presentation.selected)

    # ── Rule 9: no domain imports in workspace ───────────────────

    def test_workspace_imports_remain_presentation_only(self):
        """workspace.py import lines must not contain domain modules."""
        with open("ui/configurator_v2/workspace.py") as f:
            source = f.read()

        import_lines = [
            line for line in source.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        import_text = "\n".join(import_lines)

        forbidden = [
            "domain.",
            "manufacturing.",
            "cost_intelligence.",
            "commercial_outputs.",
            "optimization.",
            "FreeCAD",
        ]
        for token in forbidden:
            self.assertNotIn(
                token,
                import_text,
                msg=f"workspace.py must not import '{token}'",
            )

    # ── Rule 10: no engine naming ────────────────────────────────

    def test_no_engine_naming_in_inspector_integration(self):
        """set_presentation_aware_inspector must not have engine methods."""
        ws, _, _, _, _, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        engine_methods = {"start", "stop", "run", "process", "dispatch", "subscribe", "emit"}
        method_names = {
            name for name in dir(workspace)
            if not name.startswith("_")
        }
        engine_overlap = engine_methods & method_names
        self.assertEqual(
            engine_overlap, set(),
            msg=f"Workspace should not expose engine methods: {engine_overlap}",
        )

    # ── Rule 11: field names are prefixed consistently ───────────

    def test_presentation_fields_have_consistent_prefix(self):
        """Presentation group fields have 'presentation_' or 'vc_' prefix."""
        ws, interactive, vc, _, _, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives,
            selected_ids=frozenset({"d1"}),
            error_ids=frozenset({"d1"}),
        )
        synced = workspace.preview_region.interactive_components[0]
        sel = self._make_selection(ws, selection_id="d1")

        workspace.set_presentation_aware_inspector(sel, synced)
        presentation_fields = [
            f for f in workspace.inspector_read_model.fields
            if f.group == "Presentation"
        ]
        for field in presentation_fields:
            self.assertTrue(
                field.name.startswith("presentation_") or field.name.startswith("vc_"),
                msg=f"Field '{field.name}' should start with 'presentation_' or 'vc_'",
            )


if __name__ == "__main__":
    unittest.main()
