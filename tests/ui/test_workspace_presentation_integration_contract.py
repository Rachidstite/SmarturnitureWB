# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Workspace Presentation Integration Contract Tests
#
# Verifies:
# - workspace attaches synchronized presentation to interactive components
# - selected/hovered/focused states propagate
# - warning/error states propagate
# - neutral components remain neutral
# - original component identity/data preserved
# - deterministic output
# - no input mutation
# - no domain/manufacturing/cost/Qt imports
# - no engine/workflow naming
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
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


class TestWorkspacePresentationIntegrationContract(unittest.TestCase):
    """Verify workspace presentation integration."""

    @classmethod
    def _import_modules(cls):
        for key in list(sys.modules):
            if key.startswith("ui.configurator_v2"):
                del sys.modules[key]

        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt()}):
            ws = importlib.import_module("ui.configurator_v2.workspace")
            interactive = importlib.import_module("ui.configurator_v2.interactive_components")
            vc = importlib.import_module("ui.configurator_v2.visual_components")
            sync = importlib.import_module("ui.configurator_v2.presentation_synchronization")
            ps = importlib.import_module("ui.configurator_v2.presentation_state")
            pvc = importlib.import_module("ui.configurator_v2.presentation_visual_contract")
        return ws, interactive, vc, sync, ps, pvc

    # ── Rule 1: attach synchronized state to components ──────────

    def test_workspace_attaches_synchronized_state(self):
        """Workspace method attaches presentation and visual contract to interactives."""
        ws, interactive, vc, _, _, pvc = self._import_modules()

        components = (
            vc.DoorVisualComponent(id="d1"),
            vc.DoorVisualComponent(id="d2"),
        )
        interactives = interactive.build_interactive_visual_components(components)

        workspace = ws.create_configurator_v2_workspace()
        workspace.synchronize_preview_interactive_components(
            interactives,
            selected_ids=frozenset({"d1"}),
            error_ids=frozenset({"d2"}),
        )

        region = workspace.preview_region
        self.assertEqual(len(region.interactive_components), 2)

        ic1 = region.interactive_components[0]
        self.assertIsNotNone(ic1.interaction.presentation)
        self.assertTrue(ic1.interaction.presentation.selected)
        self.assertIsNotNone(ic1.interaction.visual_contract)
        self.assertEqual(
            ic1.interaction.visual_contract.outline_intent, pvc.OUTLINE_SELECTED
        )

        ic2 = region.interactive_components[1]
        self.assertIsNotNone(ic2.interaction.presentation)
        self.assertTrue(ic2.interaction.presentation.error)
        self.assertEqual(
            ic2.interaction.visual_contract.outline_intent, pvc.OUTLINE_ERROR
        )
        self.assertEqual(ic2.interaction.visual_contract.emphasis_level, pvc.EMPHASIS_CRITICAL)

    # ── Rule 2: selected ─────────────────────────────────────────

    def test_selected_receives_correct_state(self):
        """Selected component gets selected presentation and SELECTED outline."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives, selected_ids=frozenset({"d1"})
        )

        ic = workspace.preview_region.interactive_components[0]
        self.assertTrue(ic.interaction.presentation.selected)
        self.assertEqual(ic.interaction.visual_contract.outline_intent, pvc.OUTLINE_SELECTED)

    # ── Rule 3: hovered/focused ─────────────────────────────────

    def test_hovered_receives_correct_state(self):
        """Hovered component gets hovered state and HOVERED outline."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives, hovered_id="d1"
        )

        ic = workspace.preview_region.interactive_components[0]
        self.assertTrue(ic.interaction.presentation.hovered)
        self.assertEqual(ic.interaction.visual_contract.outline_intent, pvc.OUTLINE_HOVERED)

    def test_focused_receives_correct_state(self):
        """Focused component gets focused state and FOCUSED outline."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives, focused_id="d1"
        )

        ic = workspace.preview_region.interactive_components[0]
        self.assertTrue(ic.interaction.presentation.focused)
        self.assertEqual(ic.interaction.visual_contract.outline_intent, pvc.OUTLINE_FOCUSED)

    # ── Rule 4: warning/error ───────────────────────────────────

    def test_warning_receives_correct_state(self):
        """Warning component gets warning state and WARNING outline."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.PanelVisualComponent(id="p1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives, warning_ids=frozenset({"p1"})
        )

        ic = workspace.preview_region.interactive_components[0]
        self.assertTrue(ic.interaction.presentation.warning)
        self.assertEqual(ic.interaction.visual_contract.outline_intent, pvc.OUTLINE_WARNING)

    def test_error_receives_correct_dominant(self):
        """Error component gets error dominant and CRITICAL emphasis."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.PanelVisualComponent(id="p1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives, error_ids=frozenset({"p1"})
        )

        ic = workspace.preview_region.interactive_components[0]
        self.assertTrue(ic.interaction.presentation.error)
        self.assertEqual(ic.interaction.visual_contract.emphasis_level, pvc.EMPHASIS_CRITICAL)

    # ── Rule 5: neutral components ──────────────────────────────

    def test_neutral_components_remain_neutral(self):
        """Components not in any flag set get presentation=None and contract=None."""
        ws, interactive, vc, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (
            vc.DoorVisualComponent(id="d1"),
            vc.DoorVisualComponent(id="d2"),
        )
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives,
            selected_ids=frozenset({"other"}),
        )

        ic1 = workspace.preview_region.interactive_components[0]
        ic2 = workspace.preview_region.interactive_components[1]

        # Both are neutral — neither in selected_ids
        self.assertIsNone(ic1.interaction.presentation)
        self.assertIsNone(ic1.interaction.visual_contract)
        self.assertIsNone(ic2.interaction.presentation)
        self.assertIsNone(ic2.interaction.visual_contract)

    # ── Rule 6: original identity preserved ─────────────────────

    def test_original_identity_preserved(self):
        """Component id, type, display_name, and interaction fields survive."""
        ws, interactive, vc, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (
            vc.DoorVisualComponent(
                id="door-1", display_name="Left Door", tooltip="Left Door"
            ),
        )
        interactives = interactive.build_interactive_visual_components(
            components,
            selected_component_id="door-1",
            show_door_swing=True,
        )
        workspace.synchronize_preview_interactive_components(
            interactives,
            selected_ids=frozenset({"door-1"}),
        )

        ic = workspace.preview_region.interactive_components[0]
        self.assertEqual(ic.component_id, "door-1")
        self.assertEqual(ic.component_type, "DOOR")
        self.assertEqual(ic.display_name, "Left Door")
        # Original interaction fields preserved
        self.assertEqual(ic.interaction.state_label, "SELECTED")
        self.assertTrue(ic.interaction.visibility.door_swing_visible)
        self.assertEqual(ic.interaction.motion.motion_hint, "swing")
        # Presentation added on top
        self.assertTrue(ic.interaction.presentation.selected)

    # ── Rule 7: deterministic ───────────────────────────────────

    def test_integration_is_deterministic(self):
        """Same inputs produce identical interactive component outputs."""
        ws, interactive, vc, _, _, _ = self._import_modules()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)

        workspace1 = ws.create_configurator_v2_workspace()
        workspace1.synchronize_preview_interactive_components(
            interactives, selected_ids=frozenset({"d1"})
        )
        workspace2 = ws.create_configurator_v2_workspace()
        workspace2.synchronize_preview_interactive_components(
            interactives, selected_ids=frozenset({"d1"})
        )

        self.assertEqual(
            workspace1.preview_region.interactive_components[0],
            workspace2.preview_region.interactive_components[0],
        )

    # ── Rule 8: no input mutation ───────────────────────────────

    def test_synchronization_does_not_mutate_originals(self):
        """Input interactive components remain unchanged after sync."""
        ws, interactive, vc, _, _, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)

        original_id = interactives[0].component_id
        original_presentation = interactives[0].interaction.presentation

        workspace.synchronize_preview_interactive_components(
            interactives, selected_ids=frozenset({"d1"})
        )

        # Original is unchanged
        self.assertEqual(interactives[0].component_id, original_id)
        self.assertIs(interactives[0].interaction.presentation, original_presentation)

        # Workspace has the NEW instance with presentation attached
        synced = workspace.preview_region.interactive_components[0]
        self.assertIsNot(synced, interactives[0])
        self.assertIsNotNone(synced.interaction.presentation)

    # ── Rule 9: no domain/scene_projection imports in workspace ─

    def test_workspace_imports_remain_presentation_only(self):
        """Workspace imports must not include domain modules."""
        ws, _, _, _, _, _ = self._import_modules()
        mod = sys.modules.get("ui.configurator_v2.workspace")

        source_file = getattr(mod, "__file__", "ui/configurator_v2/workspace.py")
        with open(source_file) as f:
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

    # ── Rule 10: no engine/workflow naming in integration ────────

    def test_no_engine_naming_in_integration(self):
        """synchronize_preview_interactive_components must not expose engine methods."""
        ws, _, _, _, _, _ = self._import_modules()
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

    # ── Rule 11: all 9 flag sets propagate through workspace ────

    def test_all_flag_sets_propagate(self):
        """All 9 flag sets propagate through workspace integration."""
        ws, interactive, vc, _, _, pvc = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (vc.DoorVisualComponent(id="c1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.synchronize_preview_interactive_components(
            interactives,
            selected_ids=frozenset({"c1"}),
            hovered_id="c1",
            focused_id="c1",
            disabled_ids=frozenset({"c1"}),
            warning_ids=frozenset({"c1"}),
            error_ids=frozenset({"c1"}),
            preview_ids=frozenset({"c1"}),
            active_ids=frozenset({"c1"}),
            muted_ids=frozenset({"c1"}),
        )

        ic = workspace.preview_region.interactive_components[0]
        p = ic.interaction.presentation
        self.assertTrue(p.selected)
        self.assertTrue(p.hovered)
        self.assertTrue(p.focused)
        self.assertTrue(p.disabled)
        self.assertTrue(p.warning)
        self.assertTrue(p.error)
        self.assertTrue(p.preview)
        self.assertTrue(p.active)
        self.assertTrue(p.muted)

        # Dominant should be error (highest severity)
        self.assertEqual(ic.interaction.visual_contract.outline_intent, pvc.OUTLINE_ERROR)


if __name__ == "__main__":
    unittest.main()
