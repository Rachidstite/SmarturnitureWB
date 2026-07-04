# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Preview Presentation Awareness Contract Tests
#
# Verifies:
# - preview exposes neutral presentation state
# - preview exposes selected/hovered/focused state
# - preview exposes warning/error visual intent
# - disabled state is dimmed/distinct
# - preview state consistent with inspector data
# - existing preview metadata preserved
# - missing data falls back safely
# - deterministic
# - no input mutation
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


class TestPreviewPresentationAwarenessContract(unittest.TestCase):
    """Verify preview presentation awareness integration."""

    @classmethod
    def _import_modules(cls):
        for key in list(sys.modules):
            if key.startswith("ui.configurator_v2"):
                del sys.modules[key]

        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt()}):
            ws = __import__("ui.configurator_v2.workspace", fromlist=["ConfiguratorV2Workspace", "create_configurator_v2_workspace"])
            interactive = __import__("ui.configurator_v2.interactive_components", fromlist=["InteractiveVisualComponent", "build_interactive_visual_components"])
            vc = __import__("ui.configurator_v2.visual_components", fromlist=["DoorVisualComponent", "PanelVisualComponent"])
            sync = __import__("ui.configurator_v2.presentation_synchronization", fromlist=["synchronize_presentation"])
            ps = __import__("ui.configurator_v2.presentation_state", fromlist=["FurniturePresentationState"])
            pvc = __import__("ui.configurator_v2.presentation_visual_contract", fromlist=["PresentationVisualContract", "OUTLINE_SELECTED", "OUTLINE_ERROR", "OUTLINE_WARNING", "OUTLINE_HOVERED", "OUTLINE_DISABLED", "OPACITY_DIM", "EMPHASIS_HIGH", "EMPHASIS_CRITICAL"])
        return ws, interactive, vc, sync, ps, pvc

    def _build_and_sync(self, ws, interactive, vc, components, **flags):
        workspace = ws.create_configurator_v2_workspace()
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(interactives, **flags)
        return workspace

    # ── Rule 1: neutral presentation ─────────────────────────────

    def test_neutral_state_shows_no_sync_section(self):
        """Preview with no synchronized components shows no Presentation Sync row."""
        ws, interactive, vc, _, _, _ = self._import_modules()
        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace = ws.create_configurator_v2_workspace()
        # Use set_preview_interactive_components — no sync
        workspace.set_preview_interactive_components(interactives)

        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertNotIn("Presentation Sync", render_text)

    def test_neutral_via_sync_shows_no_sync_section(self):
        """Components synced with no flags produce no Presentation Sync section."""
        ws, interactive, vc, _, _, _ = self._import_modules()
        workspace = self._build_and_sync(ws, interactive, vc, (vc.DoorVisualComponent(id="d1"),))
        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertNotIn("Presentation Sync", render_text)
        # Component still appears in interactive section
        self.assertIn("Interactive Components: 1 active", render_text)

    # ── Rule 2: selected state ───────────────────────────────────

    def test_selected_appears_in_preview(self):
        """Preview shows selected presentation data."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = self._build_and_sync(
            ws, interactive, vc,
            (vc.DoorVisualComponent(id="d1"),),
            selected_ids=frozenset({"d1"}),
        )
        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertIn("Presentation Sync", render_text)
        self.assertIn("d1", render_text)
        self.assertIn("selected", render_text)
        self.assertIn(pvc.OUTLINE_SELECTED, render_text)

    # ── Rule 3: hovered/focused ──────────────────────────────────

    def test_hovered_appears_in_preview(self):
        """Preview shows hovered state."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = self._build_and_sync(
            ws, interactive, vc,
            (vc.DoorVisualComponent(id="d1"),),
            hovered_id="d1",
        )
        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertIn("hovered", render_text)
        self.assertIn(pvc.OUTLINE_HOVERED, render_text)

    def test_focused_appears_in_preview(self):
        """Preview shows focused state."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = self._build_and_sync(
            ws, interactive, vc,
            (vc.DoorVisualComponent(id="d1"),),
            focused_id="d1",
        )
        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertIn("focused", render_text)
        self.assertIn(pvc.OUTLINE_FOCUSED, render_text)

    # ── Rule 4: warning/error ────────────────────────────────────

    def test_warning_appears_in_preview(self):
        """Preview shows warning dominant and HIGH emphasis."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = self._build_and_sync(
            ws, interactive, vc,
            (vc.PanelVisualComponent(id="p1"),),
            warning_ids=frozenset({"p1"}),
        )
        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertIn("warning", render_text)
        self.assertIn(pvc.EMPHASIS_HIGH, render_text)
        self.assertIn(pvc.OUTLINE_WARNING, render_text)

    def test_error_appears_in_preview(self):
        """Preview shows error dominant and CRITICAL emphasis."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = self._build_and_sync(
            ws, interactive, vc,
            (vc.PanelVisualComponent(id="p1"),),
            error_ids=frozenset({"p1"}),
        )
        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertIn("error", render_text)
        self.assertIn(pvc.EMPHASIS_CRITICAL, render_text)
        self.assertIn(pvc.OUTLINE_ERROR, render_text)

    # ── Rule 5: disabled state ───────────────────────────────────

    def test_disabled_appears_dim_in_preview(self):
        """Preview shows disabled state with DIM opacity."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = self._build_and_sync(
            ws, interactive, vc,
            (vc.DoorVisualComponent(id="x1"),),
            disabled_ids=frozenset({"x1"}),
        )
        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertIn("disabled", render_text)
        self.assertIn(pvc.OUTLINE_DISABLED, render_text)
        self.assertIn(pvc.OPACITY_DIM, render_text)

    # ── Rule 6: consistency with synchronized data ───────────────

    def test_preview_state_matches_synchronized_data(self):
        """Preview render text reflects the synchronized presentation state."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = self._build_and_sync(
            ws, interactive, vc,
            (vc.DoorVisualComponent(id="d1"), vc.PanelVisualComponent(id="p1")),
            selected_ids=frozenset({"d1"}),
            error_ids=frozenset({"p1"}),
        )
        render_text = "\n".join(workspace.preview_region.render_rows)
        # First component selected
        self.assertIn("d1", render_text)
        self.assertIn("selected", render_text)
        self.assertIn(pvc.OUTLINE_SELECTED, render_text)
        # Second component error
        self.assertIn("p1", render_text)
        self.assertIn("error", render_text)
        self.assertIn(pvc.OUTLINE_ERROR, render_text)

    def test_preview_and_inspector_consistent(self):
        """Preview and inspector show the same dominant flag for the same component."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = self._build_and_sync(
            ws, interactive, vc,
            (vc.DoorVisualComponent(id="d1"),),
            selected_ids=frozenset({"d1"}),
        )
        # Inspector
        sel = ws.ConfiguratorSelection(
            selection_type="DOOR", selection_id="d1", display_name="Door"
        )
        synced = workspace.preview_region.interactive_components[0]
        workspace.set_presentation_aware_inspector(sel, synced)
        insp_fields = {f.name: f.value for f in workspace.inspector_read_model.fields}

        # Preview
        render_text = "\n".join(workspace.preview_region.render_rows)

        # Both show "selected"
        self.assertEqual(insp_fields.get("presentation_dominant"), "selected")
        self.assertIn("selected", render_text)

    # ── Rule 7: existing metadata preserved ──────────────────────

    def test_existing_preview_metadata_preserved(self):
        """Existing preview fields (title, mode, count) remain after sync."""
        ws, interactive, vc, _, _, _ = self._import_modules()
        workspace = self._build_and_sync(
            ws, interactive, vc,
            (vc.DoorVisualComponent(id="d1"),),
            selected_ids=frozenset({"d1"}),
        )
        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertIn("Preview Title", render_text)
        self.assertIn("Preview Mode", render_text)
        self.assertIn("Node Count", render_text)

    # ── Rule 8: missing data fallback ────────────────────────────

    def test_no_interactive_components_shows_no_presentation_section(self):
        """Preview with no interactive components shows no Presentation Sync."""
        ws, interactive, vc, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()
        workspace.synchronize_preview_interactive_components(
            interactive.build_interactive_visual_components(()),
        )
        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertNotIn("Presentation Sync", render_text)

    # ── Rule 9: deterministic ────────────────────────────────────

    def test_preview_render_is_deterministic(self):
        """Same inputs produce same preview render rows."""
        ws, interactive, vc, _, _, _ = self._import_modules()

        def _get_render():
            w = self._build_and_sync(
                ws, interactive, vc,
                (vc.DoorVisualComponent(id="d1"),),
                selected_ids=frozenset({"d1"}),
            )
            return list(w.preview_region.render_rows)

        self.assertEqual(_get_render(), _get_render())

    # ── Rule 10: no input mutation ───────────────────────────────

    def test_synchronize_does_not_mutate_originals(self):
        """Original interactive components are unchanged after sync into preview."""
        ws, interactive, vc, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        original_id = interactives[0].component_id

        workspace.synchronize_preview_interactive_components(
            interactives, selected_ids=frozenset({"d1"})
        )

        self.assertEqual(interactives[0].component_id, original_id)
        # Workspace has NEW instances
        synced = workspace.preview_region.interactive_components[0]
        self.assertIsNot(synced, interactives[0])

    # ── Rule 11: no domain imports ───────────────────────────────

    def test_workspace_imports_remain_presentation_only(self):
        """workspace.py must not import domain modules."""
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

    # ── Rule 12: no engine naming ────────────────────────────────

    def test_no_engine_naming_in_preview_integration(self):
        """PreviewRegion must not have engine methods."""
        ws, _, _, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        engine_methods = {"start", "stop", "run", "process", "dispatch", "subscribe", "emit"}
        method_names = {
            name for name in dir(workspace.preview_region)
            if not name.startswith("_")
        }
        engine_overlap = engine_methods & method_names
        self.assertEqual(
            engine_overlap, set(),
            msg=f"PreviewRegion should not expose engine methods: {engine_overlap}",
        )

    # ── Rule 13: severity visible in preview ─────────────────────

    def test_severity_shown_in_preview(self):
        """Preview shows severity number for synced components."""
        ws, interactive, vc, _, _, _ = self._import_modules()
        workspace = self._build_and_sync(
            ws, interactive, vc,
            (vc.DoorVisualComponent(id="d1"),),
            error_ids=frozenset({"d1"}),
        )
        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertIn("sev=50", render_text)

    # ── Rule 14: limited to 5 components ─────────────────────────

    def test_preview_shows_up_to_five_synced_components(self):
        """Preview only shows up to 5 synced components in display."""
        ws, interactive, vc, _, _, _ = self._import_modules()
        many_components = tuple(
            vc.DoorVisualComponent(id=f"d{i}") for i in range(10)
        )
        workspace = self._build_and_sync(
            ws, interactive, vc,
            many_components,
            selected_ids=frozenset({f"d{i}" for i in range(10)}),
        )
        render_text = "\n".join(workspace.preview_region.render_rows)
        self.assertIn("10 component(s) synced", render_text)
        # Should show at most 5 individual lines
        component_lines = [l for l in workspace.preview_region.render_rows if l.strip().startswith("  d")]
        self.assertLessEqual(len(component_lines), 5)


if __name__ == "__main__":
    unittest.main()
