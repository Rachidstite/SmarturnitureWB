# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Furniture Presentation State Contract Tests
#
# Verifies:
# - default state is neutral
# - selected/hovered/focused/disabled states detected
# - warning and error states detected
# - multiple flags can coexist
# - error > warning > disabled > selected > hovered severity ordering
# - resolver is deterministic
# - presentation state has no business/manufacturing/cost concepts
# - existing Configurator V2 public imports remain backward compatible
# - integration with interactive_components.py is safe
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import importlib.machinery
import importlib.util
import sys
import types
import unittest
from unittest.mock import patch


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


class TestFurniturePresentationStateContract(unittest.TestCase):
    """Verify the FurniturePresentationState value-object and resolver contract."""

    @classmethod
    def _import_state_module(cls):
        """Import presentation_state directly, bypassing package __init__ chain."""
        path = "ui/configurator_v2/presentation_state.py"
        loader = importlib.machinery.SourceFileLoader(
            "ui.configurator_v2.presentation_state",
            path,
        )
        spec = importlib.machinery.ModuleSpec(
            "ui.configurator_v2.presentation_state", loader, origin=path
        )
        mod = importlib.util.module_from_spec(spec)
        # Pre-seed the parent package so __init__.py doesn't load
        parent = types.ModuleType("ui.configurator_v2")
        parent.__path__ = ["ui/configurator_v2"]
        with patch.dict(sys.modules, {"ui.configurator_v2": parent}):
            sys.modules["ui.configurator_v2.presentation_state"] = mod
            loader.exec_module(mod)
        return mod

    @classmethod
    def _import_with_qt(cls):
        """Import modules that need the qt_compat patch."""
        # Remove any stale stub modules from presentation_state direct-load
        for key in list(sys.modules):
            if key.startswith("ui.configurator_v2"):
                del sys.modules[key]
        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt_module()}):
            interactive = importlib.import_module("ui.configurator_v2.interactive_components")
            vc = importlib.import_module("ui.configurator_v2.visual_components")
            init = importlib.import_module("ui.configurator_v2")
        return interactive, vc, init

    # ── Rule 1: default state is neutral ──────────────────────────

    def test_default_state_is_neutral(self):
        """A default-constructed FurniturePresentationState is neutral."""
        ps = self._import_state_module()
        state = ps.FurniturePresentationState()
        self.assertTrue(state.is_neutral)
        self.assertEqual(state.dominant_flag, "neutral")
        self.assertEqual(state.visual_severity, 0)
        self.assertEqual(state.active_flags, ())

    def test_neutral_from_resolver_with_no_inputs(self):
        """Resolve with an ID but no inputs produces neutral state."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state("any-id")
        self.assertTrue(state.is_neutral)

    def test_neutral_from_resolver_empty_id(self):
        """Resolve with empty component_id produces neutral (no match)."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "other",
            selected_ids=frozenset({"selected-one"}),
        )
        self.assertTrue(state.is_neutral)

    # ── Rule 2: selected state ────────────────────────────────────

    def test_selected_detected(self):
        """Component in selected_ids gets selected=True."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            selected_ids=frozenset({"c1", "c3"}),
        )
        self.assertTrue(state.selected)
        self.assertIn("selected", state.active_flags)

    def test_selected_absent_when_not_in_set(self):
        """Component not in selected_ids gets selected=False."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c2",
            selected_ids=frozenset({"c1"}),
        )
        self.assertFalse(state.selected)

    # ── Rule 3: hovered state ─────────────────────────────────────

    def test_hovered_detected(self):
        """Component matching hovered_id gets hovered=True."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            hovered_id="c1",
        )
        self.assertTrue(state.hovered)

    def test_hovered_only_matches_single_id(self):
        """Only the exact hovered_id match gets hovered=True."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c2",
            hovered_id="c1",
        )
        self.assertFalse(state.hovered)

    def test_hovered_empty_string_no_match(self):
        """Empty hovered_id does not match any component."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "",
            hovered_id="",
        )
        self.assertFalse(state.hovered)

    # ── Rule 4: focused state ─────────────────────────────────────

    def test_focused_detected(self):
        """Component matching focused_id gets focused=True."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            focused_id="c1",
        )
        self.assertTrue(state.focused)

    def test_focused_only_matches_single_id(self):
        """Only the exact focused_id match gets focused=True."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c2",
            focused_id="c1",
        )
        self.assertFalse(state.focused)

    # ── Rule 5: disabled state ────────────────────────────────────

    def test_disabled_detected(self):
        """Component in disabled_ids gets disabled=True."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            disabled_ids=frozenset({"c1", "c2"}),
        )
        self.assertTrue(state.disabled)

    def test_disabled_absent_when_not_in_set(self):
        """Component not in disabled_ids gets disabled=False."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c3",
            disabled_ids=frozenset({"c1"}),
        )
        self.assertFalse(state.disabled)

    # ── Rule 6: warning and error states ──────────────────────────

    def test_warning_detected(self):
        """Component in warning_ids gets warning=True."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            warning_ids=frozenset({"c1"}),
        )
        self.assertTrue(state.warning)

    def test_error_detected(self):
        """Component in error_ids gets error=True."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            error_ids=frozenset({"c1"}),
        )
        self.assertTrue(state.error)

    def test_preview_detected(self):
        """Component in preview_ids gets preview=True."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            preview_ids=frozenset({"c1"}),
        )
        self.assertTrue(state.preview)

    def test_active_detected(self):
        """Component in active_ids gets active=True."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            active_ids=frozenset({"c1"}),
        )
        self.assertTrue(state.active)

    def test_muted_detected(self):
        """Component in muted_ids gets muted=True."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            muted_ids=frozenset({"c1"}),
        )
        self.assertTrue(state.muted)

    # ── Rule 7: multiple flags coexist ────────────────────────────

    def test_multiple_flags_can_coexist(self):
        """A component can have several flags active simultaneously."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            selected_ids=frozenset({"c1"}),
            hovered_id="c1",
            focused_id="c1",
            warning_ids=frozenset({"c1"}),
        )
        self.assertTrue(state.selected)
        self.assertTrue(state.hovered)
        self.assertTrue(state.focused)
        self.assertTrue(state.warning)
        self.assertEqual(len(state.active_flags), 4)

    # ── Rule 8: error > warning severity ──────────────────────────

    def test_error_higher_severity_than_warning(self):
        """error has higher visual_severity than warning."""
        ps = self._import_state_module()

        error_state = ps.resolve_presentation_state(
            "c1",
            error_ids=frozenset({"c1"}),
        )
        warning_state = ps.resolve_presentation_state(
            "c1",
            warning_ids=frozenset({"c1"}),
        )
        self.assertGreater(
            error_state.visual_severity,
            warning_state.visual_severity,
        )
        self.assertEqual(error_state.dominant_flag, "error")
        self.assertEqual(warning_state.dominant_flag, "warning")

    def test_error_dominates_over_warning(self):
        """When both error and warning are set, dominant flag is error."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            warning_ids=frozenset({"c1"}),
            error_ids=frozenset({"c1"}),
        )
        self.assertEqual(state.dominant_flag, "error")
        self.assertTrue(state.warning)
        self.assertTrue(state.error)

    # ── Rule 9: disabled priority ─────────────────────────────────

    def test_disabled_priority_over_selected(self):
        """disabled has higher severity than selected."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            selected_ids=frozenset({"c1"}),
            disabled_ids=frozenset({"c1"}),
        )
        self.assertEqual(state.dominant_flag, "disabled")
        self.assertGreater(
            state.visual_severity,
            ps.resolve_presentation_state(
                "c1",
                selected_ids=frozenset({"c1"}),
            ).visual_severity,
        )

    def test_disabled_priority_over_hovered(self):
        """disabled has higher severity than hovered."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            hovered_id="c1",
            disabled_ids=frozenset({"c1"}),
        )
        self.assertEqual(state.dominant_flag, "disabled")

    # ── Rule 10: resolver is deterministic ────────────────────────

    def test_resolver_is_deterministic(self):
        """Same inputs always produce the same result."""
        ps = self._import_state_module()
        params = dict(
            selected_ids=frozenset({"a", "b"}),
            hovered_id="b",
            focused_id="c",
            disabled_ids=frozenset({"d"}),
            warning_ids=frozenset({"a"}),
            error_ids=frozenset({"e"}),
            preview_ids=frozenset({"p"}),
            active_ids=frozenset({"q"}),
            muted_ids=frozenset({"r"}),
        )
        results = [
            ps.resolve_presentation_state("a", **params)
            for _ in range(5)
        ]
        for i in range(1, len(results)):
            self.assertEqual(results[0], results[i])

    def test_batch_resolver_preserves_order(self):
        """resolve_presentation_states maintains 1:1 order with input IDs."""
        ps = self._import_state_module()
        ids = ("a", "b", "c")
        states = ps.resolve_presentation_states(
            ids,
            selected_ids=frozenset({"a"}),
        )
        self.assertEqual(len(states), 3)
        self.assertTrue(states[0].selected)
        self.assertFalse(states[1].selected)
        self.assertFalse(states[2].selected)

    # ── Rule 11: no business/manufacturing/cost concepts ──────────

    def test_no_business_manufacturing_cost_attributes(self):
        """FurniturePresentationState must not carry domain attributes."""
        ps = self._import_state_module()
        state = ps.FurniturePresentationState()

        forbidden = {
            "material_cost",
            "manufacturing_time",
            "cnc_path",
            "nesting",
            "optimization_hint",
            "engineering_status",
            "commercial_status",
            "supplier",
            "part_number",
            "bom_entry",
        }
        for attr in forbidden:
            self.assertFalse(
                hasattr(state, attr),
                msg=f"FurniturePresentationState should not have attribute '{attr}'",
            )

    def test_presentation_state_imports_no_domain_modules(self):
        """presentation_state.py must not import domain modules."""
        source_file = "ui/configurator_v2/presentation_state.py"
        with open(source_file) as f:
            source = f.read()

        forbidden_imports = [
            "domain.",
            "manufacturing.",
            "cost_intelligence.",
            "commercial_outputs.",
            "FreeCAD",
            "SceneGraph",
            "scene_projection",
            "visual_components",
        ]
        for token in forbidden_imports:
            self.assertNotIn(
                token,
                source,
                msg=f"presentation_state.py must not import '{token}'",
            )

    # ── Rule 12: neutral_presentation_state singleton ─────────────

    def test_neutral_singleton_is_consistent(self):
        """neutral_presentation_state() always returns a neutral state."""
        ps = self._import_state_module()
        n1 = ps.neutral_presentation_state()
        n2 = ps.neutral_presentation_state()
        self.assertIs(n1, n2)
        self.assertTrue(n1.is_neutral)

    # ── Rule 13: descriptor pairs ─────────────────────────────────

    def test_descriptor_pairs_none_or_neutral(self):
        """presentation_state_descriptor_pairs returns () for None or neutral."""
        ps = self._import_state_module()
        self.assertEqual(ps.presentation_state_descriptor_pairs(None), ())
        self.assertEqual(
            ps.presentation_state_descriptor_pairs(ps.FurniturePresentationState()),
            (),
        )

    def test_descriptor_pairs_active_flags(self):
        """Non-neutral state yields descriptor pairs."""
        ps = self._import_state_module()
        state = ps.resolve_presentation_state(
            "c1",
            selected_ids=frozenset({"c1"}),
            error_ids=frozenset({"c1"}),
        )
        pairs = dict(ps.presentation_state_descriptor_pairs(state))
        self.assertEqual(pairs.get("presentation_selected"), "yes")
        self.assertEqual(pairs.get("presentation_error"), "yes")
        self.assertEqual(pairs.get("presentation_dominant"), "error")
        self.assertEqual(pairs.get("presentation_severity"), "50")

    # ── Rule 14: existing backward compatibility ──────────────────

    def test_visual_component_library_still_imports(self):
        """Existing __init__.py imports still work with new exports."""
        _, vc, init_mod = self._import_with_qt()

        # Verify core types still accessible
        self.assertTrue(hasattr(vc, "VisualComponent"))
        self.assertTrue(hasattr(vc, "DoorVisualComponent"))
        self.assertTrue(hasattr(init_mod, "VisualComponent"))
        self.assertTrue(hasattr(init_mod, "build_visual_components"))

    def test_interactive_components_still_work(self):
        """InteractiveComponent construction still works with presentation=None."""
        interactive, vc, _ = self._import_with_qt()

        ic = interactive.InteractiveVisualComponent(
            component_id="d1",
            component_type="DOOR",
            interaction=interactive.ComponentInteractionState(
                state_label="SELECTED",
                presentation=None,
            ),
        )
        self.assertEqual(ic.component_id, "d1")
        self.assertIsNone(ic.interaction.presentation)

    def test_interactive_component_with_presentation(self):
        """Interactive component can carry a presentation state."""
        ps = self._import_state_module()
        interactive, vc, _ = self._import_with_qt()

        pstate = ps.resolve_presentation_state(
            "d1",
            selected_ids=frozenset({"d1"}),
            warning_ids=frozenset({"d1"}),
        )
        ic = interactive.InteractiveVisualComponent(
            component_id="d1",
            component_type="DOOR",
            interaction=interactive.ComponentInteractionState(
                state_label="SELECTED",
                presentation=pstate,
            ),
        )
        self.assertIs(ic.interaction.presentation, pstate)
        self.assertTrue(pstate.selected)
        self.assertTrue(pstate.warning)
        self.assertEqual(pstate.dominant_flag, "warning")

    # ── Rule 15: type validation ──────────────────────────────────

    def test_type_validation_selected(self):
        """Non-bool selected raises TypeError."""
        ps = self._import_state_module()
        with self.assertRaises(TypeError):
            ps.FurniturePresentationState(selected="yes")  # type: ignore

    def test_type_validation_disabled(self):
        """Non-bool disabled raises TypeError."""
        ps = self._import_state_module()
        with self.assertRaises(TypeError):
            ps.FurniturePresentationState(disabled=1)  # type: ignore

    # ── Rule 16: PRESENTATION_FLAGS const ─────────────────────────

    def test_presentation_flags_are_complete(self):
        """PRESENTATION_FLAGS contains exactly the 9 required flags."""
        ps = self._import_state_module()
        expected = {
            "selected",
            "hovered",
            "focused",
            "disabled",
            "warning",
            "error",
            "preview",
            "active",
            "muted",
        }
        self.assertEqual(expected, set(ps.PRESENTATION_FLAGS))


if __name__ == "__main__":
    unittest.main()
