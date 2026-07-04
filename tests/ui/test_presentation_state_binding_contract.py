# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Presentation State Binding Contract Tests
#
# Verifies:
# - resolver returns neutral for unknown components
# - selected/hovered/focused ids map correctly
# - warning/error ids map correctly
# - multiple states coexist
# - error > warning > disabled severity ordering
# - bind_to_interactive attaches states without side effects
# - no domain/manufacturing/cost imports
# - deterministic output
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
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


class _FakeNode:
    def __init__(
        self,
        node_id,
        label,
        role_name,
        x,
        y,
        z,
        width,
        depth,
        height,
        *,
        visible=True,
        selectable=True,
        metadata=None,
    ):
        self.identity = types.SimpleNamespace(key=node_id)
        self.node_type = role_name
        self.label = label
        self.name = label
        self.visible = visible
        self.selectable = selectable
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.depth = depth
        self.height = height
        self.metadata = metadata or {}
        self.role = types.SimpleNamespace(name=role_name)


class _FakeSceneGraph:
    def __init__(self, nodes):
        self._nodes = list(nodes)

    def all_nodes(self):
        return list(self._nodes)


class TestPresentationStateBindingContract(unittest.TestCase):
    """Verify the PresentationStateResolver binding contract."""

    @classmethod
    def _import_modules(cls):
        """Import all needed modules under the qt_compat patch."""
        for key in list(sys.modules):
            if key.startswith("ui.configurator_v2"):
                del sys.modules[key]
        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt_module()}):
            binding = importlib.import_module("ui.configurator_v2.presentation_binding")
            interactive = importlib.import_module("ui.configurator_v2.interactive_components")
            vc = importlib.import_module("ui.configurator_v2.visual_components")
            adapters = importlib.import_module("ui.configurator_v2.projection_adapters")
        return binding, interactive, vc, adapters

    # ── Rule 1: neutral for unknown components ────────────────────

    def test_neutral_for_unknown_component(self):
        """Resolver returns neutral state for an unknown component ID."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            selected_ids=frozenset({"c1"}),
        )
        state = resolver.resolve("unknown-id")
        self.assertTrue(state.is_neutral)

    def test_neutral_when_no_flags_set(self):
        """Resolver with no flag sets returns neutral for every ID."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver()
        state = resolver.resolve("any-id")
        self.assertTrue(state.is_neutral)

    # ── Rule 2: selected ids ──────────────────────────────────────

    def test_selected_id_becomes_selected_state(self):
        """Selected component IDs become selected=True."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            selected_ids=frozenset({"d1", "d2"}),
        )
        self.assertTrue(resolver.resolve("d1").selected)
        self.assertTrue(resolver.resolve("d2").selected)
        self.assertFalse(resolver.resolve("d3").selected)

    # ── Rule 3: hovered id ────────────────────────────────────────

    def test_hovered_id_becomes_hovered_state(self):
        """Hovered component ID becomes hovered=True."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(hovered_id="d1")
        self.assertTrue(resolver.resolve("d1").hovered)
        self.assertFalse(resolver.resolve("d2").hovered)

    # ── Rule 4: focused id ────────────────────────────────────────

    def test_focused_id_becomes_focused_state(self):
        """Focused component ID becomes focused=True."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(focused_id="d1")
        self.assertTrue(resolver.resolve("d1").focused)
        self.assertFalse(resolver.resolve("d2").focused)

    # ── Rule 5: warning/error ids ─────────────────────────────────

    def test_warning_id_maps_correctly(self):
        """Warning component IDs become warning=True."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            warning_ids=frozenset({"p1"}),
        )
        self.assertTrue(resolver.resolve("p1").warning)
        self.assertFalse(resolver.resolve("p2").warning)

    def test_error_id_maps_correctly(self):
        """Error component IDs become error=True."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            error_ids=frozenset({"p1"}),
        )
        self.assertTrue(resolver.resolve("p1").error)
        self.assertFalse(resolver.resolve("p2").error)

    def test_preview_id_maps_correctly(self):
        """Preview component IDs become preview=True."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            preview_ids=frozenset({"p1"}),
        )
        self.assertTrue(resolver.resolve("p1").preview)

    def test_active_id_maps_correctly(self):
        """Active component IDs become active=True."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            active_ids=frozenset({"a1"}),
        )
        self.assertTrue(resolver.resolve("a1").active)

    def test_muted_id_maps_correctly(self):
        """Muted component IDs become muted=True."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            muted_ids=frozenset({"m1"}),
        )
        self.assertTrue(resolver.resolve("m1").muted)

    def test_disabled_id_maps_correctly(self):
        """Disabled component IDs become disabled=True."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            disabled_ids=frozenset({"x1"}),
        )
        self.assertTrue(resolver.resolve("x1").disabled)

    # ── Rule 6: multiple states coexist ───────────────────────────

    def test_multiple_states_coexist(self):
        """A component in multiple flag sets gets multiple flags."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            selected_ids=frozenset({"c1"}),
            hovered_id="c1",
            warning_ids=frozenset({"c1"}),
        )
        state = resolver.resolve("c1")
        self.assertTrue(state.selected)
        self.assertTrue(state.hovered)
        self.assertTrue(state.warning)
        self.assertGreaterEqual(len(state.active_flags), 3)

    # ── Rule 7: error dominant over warning ───────────────────────

    def test_error_dominant_over_warning(self):
        """Error remains visually dominant over warning in binding."""
        binding, _, _, _ = self._import_modules()

        both_resolver = binding.PresentationStateResolver(
            warning_ids=frozenset({"c1"}),
            error_ids=frozenset({"c1"}),
        )
        warn_only_resolver = binding.PresentationStateResolver(
            warning_ids=frozenset({"c1"}),
        )
        both = both_resolver.resolve("c1")
        warn_only = warn_only_resolver.resolve("c1")

        self.assertEqual(both.dominant_flag, "error")
        self.assertGreater(both.visual_severity, warn_only.visual_severity)

    # ── Rule 8: disabled dominant over selected/hovered ───────────

    def test_disabled_dominant_over_selected(self):
        """Disabled remains visually dominant when also selected."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            selected_ids=frozenset({"c1"}),
            disabled_ids=frozenset({"c1"}),
        )
        state = resolver.resolve("c1")
        self.assertEqual(state.dominant_flag, "disabled")

    def test_disabled_dominant_over_hovered(self):
        """Disabled remains visually dominant when also hovered."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            hovered_id="c1",
            disabled_ids=frozenset({"c1"}),
        )
        state = resolver.resolve("c1")
        self.assertEqual(state.dominant_flag, "disabled")

    def test_disabled_dominant_over_focused(self):
        """Disabled remains visually dominant when also focused."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            focused_id="c1",
            disabled_ids=frozenset({"c1"}),
        )
        state = resolver.resolve("c1")
        self.assertEqual(state.dominant_flag, "disabled")

    # ── Rule 9: deterministic ─────────────────────────────────────

    def test_resolver_is_deterministic(self):
        """Same resolver with same IDs produces same output every call."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            selected_ids=frozenset({"a", "b"}),
            hovered_id="b",
            warning_ids=frozenset({"a"}),
            disabled_ids=frozenset({"c"}),
        )
        states_a = [resolver.resolve("a") for _ in range(5)]
        states_b = [resolver.resolve("b") for _ in range(5)]
        for i in range(1, 5):
            self.assertEqual(states_a[0], states_a[i])
            self.assertEqual(states_b[0], states_b[i])

    # ── Rule 10: resolve_all preserves order ──────────────────────

    def test_resolve_all_preserves_order(self):
        """Batch resolve maintains 1:1 correspondence with input IDs."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver(
            selected_ids=frozenset({"a"}),
            error_ids=frozenset({"b"}),
        )
        ids = ("c", "a", "b", "d")
        states = resolver.resolve_all(ids)
        self.assertEqual(len(states), 4)
        self.assertTrue(states[0].is_neutral)
        self.assertTrue(states[1].selected)
        self.assertTrue(states[2].error)
        self.assertTrue(states[3].is_neutral)

    # ── Rule 11: bind_to_interactive ──────────────────────────────

    def test_bind_to_interactive_empty(self):
        """bind_to_interactive handles empty input."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver()
        result = resolver.bind_to_interactive(())
        self.assertEqual(result, ())

    def test_bind_to_interactive_attaches_presentation(self):
        """bind_to_interactive attaches presentation states to interactives."""
        binding, interactive, vc, _ = self._import_modules()

        components = (
            vc.DoorVisualComponent(id="d1"),
            vc.DoorVisualComponent(id="d2"),
        )
        interactives = interactive.build_interactive_visual_components(components)

        resolver = binding.PresentationStateResolver(
            selected_ids=frozenset({"d1"}),
            warning_ids=frozenset({"d2"}),
        )
        bound = resolver.bind_to_interactive(interactives)

        self.assertEqual(len(bound), 2)
        self.assertEqual(bound[0].component_id, "d1")
        self.assertEqual(bound[1].component_id, "d2")

        # d1 is selected
        self.assertIsNotNone(bound[0].interaction.presentation)
        self.assertTrue(bound[0].interaction.presentation.selected)
        self.assertFalse(bound[0].interaction.presentation.warning)

        # d2 has warning
        self.assertIsNotNone(bound[1].interaction.presentation)
        self.assertFalse(bound[1].interaction.presentation.selected)
        self.assertTrue(bound[1].interaction.presentation.warning)

    def test_bind_to_interactive_preserves_other_state(self):
        """bind_to_interactive preserves existing interaction state fields."""
        binding, interactive, vc, _ = self._import_modules()

        components = (
            vc.DoorVisualComponent(id="d1", tooltip="Left Door"),
        )
        interactives = interactive.build_interactive_visual_components(
            components,
            selected_component_id="d1",
            show_door_swing=True,
        )
        original_tooltip = interactives[0].interaction.tooltip

        resolver = binding.PresentationStateResolver(
            warning_ids=frozenset({"d1"}),
        )
        bound = resolver.bind_to_interactive(interactives)

        # Original interaction fields preserved
        self.assertEqual(bound[0].interaction.tooltip, original_tooltip)
        self.assertEqual(bound[0].interaction.state_label, "SELECTED")
        self.assertTrue(bound[0].interaction.visibility.door_swing_visible)

        # Presentation attached (warning from resolver, not selected)
        self.assertTrue(bound[0].interaction.presentation.warning)
        self.assertFalse(bound[0].interaction.presentation.selected)

    def test_bind_to_interactive_skips_neutral(self):
        """bind_to_interactive sets presentation=None for neutral components."""
        binding, interactive, vc, _ = self._import_modules()

        components = (vc.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)

        resolver = binding.PresentationStateResolver()  # no flags
        bound = resolver.bind_to_interactive(interactives)

        self.assertIsNone(bound[0].interaction.presentation)

    # ── Rule 12: from_visual_components_and_ids ───────────────────

    def test_from_visual_components_and_ids(self):
        """Static factory resolves states for VisualComponents by ID."""
        binding, _, vc, _ = self._import_modules()

        components = (
            vc.DoorVisualComponent(id="d1"),
            vc.PanelVisualComponent(id="p1"),
            vc.DrawerVisualComponent(id="dr1"),
        )
        states = binding.PresentationStateResolver.from_visual_components_and_ids(
            components,
            selected_ids=frozenset({"d1", "dr1"}),
            error_ids=frozenset({"p1"}),
        )
        self.assertEqual(len(states), 3)
        self.assertTrue(states[0].selected)
        self.assertTrue(states[1].error)
        self.assertTrue(states[2].selected)

    # ── Rule 13: no domain/manufacturing/cost imports ─────────────

    def test_binding_imports_no_domain_modules(self):
        """presentation_binding.py must not import domain modules."""
        with open("ui/configurator_v2/presentation_binding.py") as f:
            source = f.read()

        forbidden = [
            "domain.",
            "manufacturing.",
            "cost_intelligence.",
            "commercial_outputs.",
            "optimization.",
            "FreeCAD",
            "SceneGraph",
        ]
        for token in forbidden:
            self.assertNotIn(
                token,
                source,
                msg=f"presentation_binding.py must not import '{token}'",
            )

    # ── Rule 14: type validation ──────────────────────────────────

    def test_resolver_validates_frozenset_args(self):
        """Non-frozenset args are converted or raise."""
        binding, _, _, _ = self._import_modules()
        # list and set are accepted (converted)
        r1 = binding.PresentationStateResolver(selected_ids={"a", "b"})
        self.assertIsInstance(r1.selected_ids, frozenset)
        self.assertIn("a", r1.selected_ids)

        r2 = binding.PresentationStateResolver(selected_ids=["a"])
        self.assertIsInstance(r2.selected_ids, frozenset)

    def test_resolver_validates_hovered_id(self):
        """Non-string hovered_id raises TypeError."""
        binding, _, _, _ = self._import_modules()
        with self.assertRaises(TypeError):
            binding.PresentationStateResolver(hovered_id=42)  # type: ignore

    # ── Rule 15: resolver is @dataclass, not an engine ────────────

    def test_resolver_is_dataclass_not_engine(self):
        """PresentationStateResolver must be a simple dataclass, not an engine."""
        binding, _, _, _ = self._import_modules()
        resolver = binding.PresentationStateResolver()

        # Must NOT have engine-like attributes
        self.assertFalse(hasattr(resolver, "start"))
        self.assertFalse(hasattr(resolver, "stop"))
        self.assertFalse(hasattr(resolver, "process"))
        self.assertFalse(hasattr(resolver, "dispatch"))
        self.assertFalse(hasattr(resolver, "subscribe"))
        self.assertFalse(hasattr(resolver, "emit"))


if __name__ == "__main__":
    unittest.main()
