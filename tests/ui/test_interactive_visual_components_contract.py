# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Interactive Visual Components Contract Tests
#
# Verifies:
# - presentation-only dataclasses
# - builder 1:1 mapping
# - selected/highlighted propagation
# - hardware/feature-marker/door/drawer toggles
# - preview adapter preserves interaction metadata
# - PreviewRegion storage and summary
# - Workspace setter integration
# - Service integration interaction toggle path
# - backward compatibility with visual-components-only path
# - backend object rejection
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import sys
import types
import unittest
from unittest.mock import patch


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


class TestInteractiveVisualComponentsContract(unittest.TestCase):
    """Verify interactive visual components contract."""

    @classmethod
    def _import_modules(cls):
        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt_module()}):
            scene_projection_mod = importlib.import_module("ui.configurator_v2.scene_projection")
            visual_components_mod = importlib.import_module("ui.configurator_v2.visual_components")
            styles_mod = importlib.import_module("ui.configurator_v2.furniture_visual_styles")
            interactive_mod = importlib.import_module("ui.configurator_v2.interactive_components")
            adapters_mod = importlib.import_module("ui.configurator_v2.projection_adapters")
            workspace_mod = importlib.import_module("ui.configurator_v2.workspace")
            service_mod = importlib.import_module("ui.configurator_v2.service_integration")
        return (
            scene_projection_mod,
            visual_components_mod,
            styles_mod,
            interactive_mod,
            adapters_mod,
            workspace_mod,
            service_mod,
        )

    # ── Rule 1: presentation-only ───────────────────────────────────

    def test_dataclasses_are_presentation_only(self):
        """All interaction dataclasses must not carry backend attributes."""
        *_, interactive, _, _, _ = self._import_modules()

        for cls_name in (
            "ComponentInteractionOverlay",
            "ComponentVisibilityState",
            "ComponentMotionIndicator",
            "ComponentInteractionState",
            "InteractiveVisualComponent",
        ):
            with self.subTest(cls_name=cls_name):
                cls = getattr(interactive, cls_name)
                obj = cls()
                self.assertFalse(hasattr(obj, "Shape"))
                self.assertFalse(hasattr(obj, "ViewObject"))
                self.assertFalse(hasattr(obj, "Document"))
                self.assertFalse(hasattr(obj, "node_id"))

    def test_interaction_state_enum_values(self):
        """INTERACTIVE_STATES contains exactly the required states."""
        *_, interactive, _, _, _ = self._import_modules()
        expected = frozenset({
            "NORMAL", "SELECTED", "HIGHLIGHTED", "EXPANDED",
            "COLLAPSED", "HIDDEN", "UNSUPPORTED", "STALE",
        })
        self.assertEqual(expected, frozenset(interactive.INTERACTIVE_STATES))

    def test_state_label_validator_rejects_bad_state(self):
        """ComponentInteractionState rejects invalid state labels."""
        *_, interactive, _, _, _ = self._import_modules()
        with self.assertRaises(TypeError):
            interactive.ComponentInteractionState(state_label="INVALID")

    # ── Rule 2: builder 1:1 mapping ─────────────────────────────────

    def test_builder_preserves_one_to_one_mapping(self):
        """build_interactive_visual_components returns one per input."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (
            visual.DoorVisualComponent(id="d1"),
            visual.DrawerVisualComponent(id="dr1"),
            visual.PanelVisualComponent(id="p1"),
            visual.BackPanelVisualComponent(id="bp1"),
            visual.HardwareVisualComponent(id="hw1"),
            visual.FeatureMarkerComponent(id="fm1"),
        )
        result = interactive.build_interactive_visual_components(components)
        self.assertEqual(len(result), 6)

    def test_builder_empty_input(self):
        """Empty input produces empty output."""
        *_, _, interactive, _, _, _ = self._import_modules()
        self.assertEqual(interactive.build_interactive_visual_components(()), ())

    def test_builder_rejects_non_component(self):
        """Non-VisualComponent items raise TypeError."""
        *_, _, interactive, _, _, _ = self._import_modules()
        with self.assertRaises(TypeError):
            interactive.build_interactive_visual_components(("not-a-component",))  # type: ignore

    # ── Rule 3: selected/highlighted propagation ────────────────────

    def test_selected_propagates(self):
        """selected_component_id marks the correct component as selected."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (
            visual.DoorVisualComponent(id="door-1"),
            visual.DoorVisualComponent(id="door-2"),
        )
        result = interactive.build_interactive_visual_components(
            components,
            selected_component_id="door-1",
        )
        self.assertTrue(result[0].interaction.overlay.selected)
        self.assertFalse(result[1].interaction.overlay.selected)

    def test_highlighted_propagates(self):
        """highlighted_component_id marks the correct component."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (
            visual.DoorVisualComponent(id="door-1"),
            visual.DoorVisualComponent(id="door-2"),
        )
        result = interactive.build_interactive_visual_components(
            components,
            highlighted_component_id="door-2",
        )
        self.assertFalse(result[0].interaction.overlay.highlighted)
        self.assertTrue(result[1].interaction.overlay.highlighted)

    def test_both_selected_and_highlighted(self):
        """Different ids for selected and highlighted."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (
            visual.DoorVisualComponent(id="a"),
            visual.DoorVisualComponent(id="b"),
            visual.DoorVisualComponent(id="c"),
        )
        result = interactive.build_interactive_visual_components(
            components,
            selected_component_id="a",
            highlighted_component_id="b",
        )
        self.assertTrue(result[0].interaction.overlay.selected)
        self.assertTrue(result[1].interaction.overlay.highlighted)
        self.assertFalse(result[2].interaction.overlay.selected)
        self.assertFalse(result[2].interaction.overlay.highlighted)

    # ── Rule 4: hardware visibility toggle ──────────────────────────

    def test_hardware_visible_toggle(self):
        """Hardware visibility is type-dependent."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (
            visual.HardwareVisualComponent(id="hw1"),
            visual.DoorVisualComponent(id="d1"),
            visual.PanelVisualComponent(id="p1"),
        )
        result = interactive.build_interactive_visual_components(
            components, show_hardware=True
        )
        # Hardware, Door, and Cabinet types get hardware_visible = True
        self.assertTrue(result[0].interaction.visibility.hardware_visible)
        self.assertTrue(result[1].interaction.visibility.hardware_visible)
        # Panel does not support hardware
        self.assertFalse(result[2].interaction.visibility.hardware_visible)

    def test_hardware_hidden_toggle(self):
        """show_hardware=False hides hardware even for supported types."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (visual.HardwareVisualComponent(id="hw1"),)
        result = interactive.build_interactive_visual_components(
            components, show_hardware=False
        )
        self.assertFalse(result[0].interaction.visibility.hardware_visible)

    # ── Rule 5: feature marker toggle ───────────────────────────────

    def test_feature_markers_visible_toggle(self):
        """Feature marker visibility only for FEATURE_MARKER type."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (
            visual.FeatureMarkerComponent(id="fm1"),
            visual.DoorVisualComponent(id="d1"),
        )
        result = interactive.build_interactive_visual_components(
            components, show_feature_markers=True
        )
        self.assertTrue(result[0].interaction.visibility.feature_markers_visible)
        self.assertFalse(result[1].interaction.visibility.feature_markers_visible)

    def test_feature_markers_hidden(self):
        """show_feature_markers=False hides markers."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (visual.FeatureMarkerComponent(id="fm1"),)
        result = interactive.build_interactive_visual_components(
            components, show_feature_markers=False
        )
        self.assertFalse(result[0].interaction.visibility.feature_markers_visible)

    # ── Rule 6: door swing only for doors ───────────────────────────

    def test_door_swing_only_for_doors(self):
        """door_swing_visible applies only to DOOR type."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (
            visual.DoorVisualComponent(id="d1"),
            visual.DrawerVisualComponent(id="dr1"),
            visual.PanelVisualComponent(id="p1"),
        )
        result = interactive.build_interactive_visual_components(
            components, show_door_swing=True
        )
        self.assertTrue(result[0].interaction.visibility.door_swing_visible)
        self.assertFalse(result[1].interaction.visibility.door_swing_visible)
        self.assertFalse(result[2].interaction.visibility.door_swing_visible)

    def test_door_swing_motion_hint(self):
        """Door swing sets motion_hint='swing'."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (visual.DoorVisualComponent(id="d1"),)
        result = interactive.build_interactive_visual_components(
            components, show_door_swing=True
        )
        self.assertEqual(result[0].interaction.motion.motion_hint, "swing")

    # ── Rule 7: drawer open only for drawers ────────────────────────

    def test_drawer_open_only_for_drawers(self):
        """drawer_open_visible applies only to DRAWER type."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (
            visual.DrawerVisualComponent(id="dr1"),
            visual.DoorVisualComponent(id="d1"),
        )
        result = interactive.build_interactive_visual_components(
            components, show_drawer_open=True
        )
        self.assertTrue(result[0].interaction.visibility.drawer_open_visible)
        self.assertFalse(result[1].interaction.visibility.drawer_open_visible)

    def test_drawer_open_motion_hint(self):
        """Drawer open sets motion_hint='slide'."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (visual.DrawerVisualComponent(id="dr1"),)
        result = interactive.build_interactive_visual_components(
            components, show_drawer_open=True
        )
        self.assertEqual(result[0].interaction.motion.motion_hint, "slide")

    # ── Rule 8: state label derivation ──────────────────────────────

    def test_state_label_derived_from_hidden(self):
        """Invisible components get HIDDEN state."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        # Build a component with visibility=False
        components = (
            visual.DoorVisualComponent(
                id="d1",
                visibility=False,
            ),
        )
        result = interactive.build_interactive_visual_components(components)
        self.assertEqual(result[0].interaction.state_label, "HIDDEN")

    def test_selected_overrides_hidden_for_unselected(self):
        """Normal visible component is NORMAL."""
        *_, visual, interactive, _, _, _ = self._import_modules()

        components = (visual.DoorVisualComponent(id="d1"),)
        result = interactive.build_interactive_visual_components(components)
        self.assertEqual(result[0].interaction.state_label, "NORMAL")

    # ── Rule 9: backend rejection ───────────────────────────────────

    def test_builder_rejects_backend_object(self):
        """Non-VisualComponent rejected by the builder path via preview adapter."""
        *_, _, interactive, adapters, _, _ = self._import_modules()

        # The preview adapter's _reject_backend_like_object catches this
        with self.assertRaises(TypeError):
            adapters.build_preview_read_model({"interactive_components": ("bad",)})

    # ── Rule 10: preview adapter preserves metadata ─────────────────

    def test_preview_adapter_includes_interaction_metadata(self):
        """Preview items from interactive components carry interaction metadata."""
        _, visual, _, interactive, adapters, _, _ = self._import_modules()

        components = (
            visual.DoorVisualComponent(id="door-1", display_name="Shaker Door"),
            visual.DrawerVisualComponent(id="drawer-1"),
        )
        interactives = interactive.build_interactive_visual_components(
            components,
            selected_component_id="door-1",
            show_door_swing=True,
            show_drawer_open=True,
        )
        read_model = adapters.build_preview_read_model(
            {"interactive_components": interactives}
        )

        self.assertEqual(read_model.node_count, 2)
        meta0 = dict(read_model.items[0].display_metadata)
        self.assertEqual(meta0.get("interaction_state"), "SELECTED")
        self.assertEqual(meta0.get("selected"), "yes")
        self.assertEqual(meta0.get("door_swing_visible"), "yes")
        self.assertEqual(meta0.get("motion_hint"), "swing")

    def test_preview_adapter_skips_empty_pairs(self):
        """Empty ('', 'no') pairs are filtered from metadata."""
        _, visual, _, interactive, adapters, _, _ = self._import_modules()

        components = (visual.DoorVisualComponent(id="d1"),)
        interactives = interactive.build_interactive_visual_components(components)
        read_model = adapters.build_preview_read_model(
            {"interactive_components": interactives}
        )
        meta = dict(read_model.items[0].display_metadata)
        # 'expanded' should be 'no' and filtered out
        self.assertNotIn("expanded", meta)
        # 'selected' is 'no' and filtered out
        self.assertNotIn("selected", meta)

    # ── Rule 11: backward compatibility ─────────────────────────────

    def test_backward_compatibility_visual_components_only(self):
        """Without interactive_components, the old path still works."""
        _, visual, _, _, adapters, _, _ = self._import_modules()

        components = (
            visual.DoorVisualComponent(
                id="door-1",
                material_name="Oak",
                base_color="#B9825A",
            ),
        )
        read_model = adapters.build_preview_read_model(
            {"visual_components": components}
        )
        self.assertEqual(read_model.node_count, 1)
        self.assertIn("material", dict(read_model.items[0].display_metadata))

    def test_backward_compatibility_none_source(self):
        """None source returns empty read model."""
        *_, adapters, _, _ = self._import_modules()
        read_model = adapters.build_preview_read_model(None)
        self.assertEqual(read_model.node_count, 0)
        self.assertEqual(read_model.preview_state, "Unavailable")

    # ── Rule 12: PreviewRegion stores and summarizes ────────────────

    def test_preview_region_stores_interactive_components(self):
        """PreviewRegion stores interactive_components after set_interactive_components."""
        _, visual, _, interactive, adapters, ws, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (
            visual.DoorVisualComponent(id="door-1", display_name="Shaker Door"),
            visual.DrawerVisualComponent(id="drawer-1"),
        )
        interactives = interactive.build_interactive_visual_components(
            components,
            selected_component_id="door-1",
        )
        read_model = adapters.build_preview_read_model(
            {"interactive_components": interactives}
        )
        region = workspace.preview_region
        region.set_interactive_components(interactives, read_model)

        self.assertEqual(len(region.interactive_components), 2)
        self.assertIs(region.interactive_components, interactives)

    def test_preview_region_render_shows_interaction_summary(self):
        """PreviewRegion renders interaction summary rows."""
        _, visual, _, interactive, adapters, ws, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (
            visual.DoorVisualComponent(id="door-1", display_name="Shaker Door"),
            visual.DrawerVisualComponent(id="drawer-1"),
        )
        interactives = interactive.build_interactive_visual_components(
            components,
            selected_component_id="door-1",
            highlighted_component_id="door-1",
            show_door_swing=True,
            show_drawer_open=True,
        )
        read_model = adapters.build_preview_read_model(
            {"interactive_components": interactives}
        )
        workspace.set_preview_interactive_components(interactives, read_model)

        region = workspace.preview_region
        self.assertEqual(len(region.interactive_components), 2)
        render_text = "\n".join(region.render_rows)
        self.assertIn("Interactive Components: 2 active", render_text)
        self.assertIn("Selected", render_text)
        self.assertIn("Highlighted", render_text)
        self.assertIn("door-1", render_text)

    # ── Rule 13: workspace setter ───────────────────────────────────

    def test_workspace_set_preview_interactive_components(self):
        """Workspace setter mirrors the visual components setter."""
        _, visual, _, interactive, adapters, ws, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (visual.DoorVisualComponent(id="door-1"),)
        interactives = interactive.build_interactive_visual_components(components)
        read_model = adapters.build_preview_read_model(
            {"interactive_components": interactives}
        )
        workspace.set_preview_interactive_components(interactives, read_model)

        self.assertIs(workspace.preview_read_model, read_model)
        self.assertEqual(workspace.preview_visual_components, ())
        self.assertIs(workspace.preview_region.interactive_components, interactives)

    def test_workspace_setter_auto_builds_read_model(self):
        """set_preview_interactive_components builds read_model when None."""
        _, visual, _, interactive, _, ws, _ = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()

        components = (visual.DoorVisualComponent(id="door-1"),)
        interactives = interactive.build_interactive_visual_components(components)
        workspace.set_preview_interactive_components(interactives, read_model=None)

        rm = workspace.preview_read_model
        self.assertEqual(rm.node_count, 1)
        self.assertIsNotNone(rm)
        self.assertEqual(workspace.preview_region.interactive_components, interactives)

    # ── Rule 14: service integration toggle path ────────────────────

    def test_service_integration_without_toggls_falls_back(self):
        """refresh_preview without toggles uses visual-components path."""
        *_, visual, interactive, adapters, ws, service_mod = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()
        integration = service_mod.attach_service_integration(workspace)

        # Build a scene and pass it through integration without toggles
        graph = _FakeSceneGraph(
            [
                _FakeNode(
                    "cabinet-1", "Base Cabinet", "CABINET",
                    0.0, 0.0, 0.0, 600.0, 580.0, 720.0,
                ),
            ]
        )
        source = {"scene_graph": graph, "selected_node_id": "cabinet-1", "highlight_target": "cabinet-1"}
        integration.refresh_preview(source)

        # Should have used visual_components path
        self.assertEqual(len(workspace.preview_visual_components), 1)
        self.assertEqual(workspace.preview_region.visual_components, workspace.preview_visual_components)
        self.assertEqual(len(workspace.preview_region.visual_styles), 1)

    def test_service_integration_with_toggls_uses_interactive_path(self):
        """refresh_preview with toggles builds interactive components."""
        *_, visual, interactive, adapters, ws, service_mod = self._import_modules()
        workspace = ws.create_configurator_v2_workspace()
        integration = service_mod.attach_service_integration(workspace)

        graph = _FakeSceneGraph(
            [
                _FakeNode(
                    "cabinet-1", "Base Cabinet", "CABINET",
                    0.0, 0.0, 0.0, 600.0, 580.0, 720.0,
                ),
                _FakeNode(
                    "door-1", "Left Door", "DOOR_PANEL",
                    18.0, 0.0, 0.0, 297.0, 18.0, 700.0,
                    metadata={"material": "Oak", "door_style": "shaker"},
                ),
            ]
        )
        source = {"scene_graph": graph, "selected_node_id": "door-1", "highlight_target": "door-1"}
        integration.refresh_preview(source, show_door_swing=True)

        # Should have used interactive_components path
        self.assertEqual(len(workspace.preview_region.interactive_components), 2)
        # Door should have swing enabled
        door_ic = workspace.preview_region.interactive_components[1]
        self.assertEqual(door_ic.component_type, "DOOR")
        self.assertTrue(door_ic.interaction.visibility.door_swing_visible)
        self.assertEqual(door_ic.interaction.motion.motion_hint, "swing")
        # Cabinet should not have swing
        cab_ic = workspace.preview_region.interactive_components[0]
        self.assertFalse(cab_ic.interaction.visibility.door_swing_visible)

    # ── Rule 15: interaction descriptor pairs ───────────────────────

    def test_interaction_descriptor_pairs_flat(self):
        """interaction_descriptor_pairs produces correct pairs."""
        *_, _, interactive, _, _, _ = self._import_modules()

        ic = interactive.InteractiveVisualComponent(
            component_id="d1",
            component_type="DOOR",
            display_name="Door",
            interaction=interactive.ComponentInteractionState(
                overlay=interactive.ComponentInteractionOverlay(
                    selected=True, highlighted=True
                ),
                visibility=interactive.ComponentVisibilityState(
                    door_swing_visible=True,
                ),
                motion=interactive.ComponentMotionIndicator(motion_hint="swing"),
                state_label="SELECTED",
            ),
        )
        pairs = dict(interactive.interaction_descriptor_pairs(ic))
        self.assertEqual(pairs.get("interaction_state"), "SELECTED")
        self.assertEqual(pairs.get("selected"), "yes")
        self.assertEqual(pairs.get("highlighted"), "yes")
        self.assertEqual(pairs.get("door_swing_visible"), "yes")
        self.assertEqual(pairs.get("motion_hint"), "swing")

    def test_interaction_descriptor_pairs_none(self):
        """interaction_descriptor_pairs(None) returns ()."""
        *_, _, interactive, _, _, _ = self._import_modules()
        self.assertEqual(interactive.interaction_descriptor_pairs(None), ())

    # ── Rule 16: summary label ──────────────────────────────────────

    def test_interaction_summary_label(self):
        """interaction_summary_label produces human-readable text."""
        *_, _, interactive, _, _, _ = self._import_modules()

        ic = interactive.InteractiveVisualComponent(
            component_id="d1",
            component_type="DOOR",
            display_name="Door",
            interaction=interactive.ComponentInteractionState(
                overlay=interactive.ComponentInteractionOverlay(
                    selected=True, highlighted=True
                ),
                state_label="SELECTED",
            ),
        )
        label = interactive.interaction_summary_label(ic)
        self.assertIn("DOOR", label)
        self.assertIn("SELECTED", label)
        self.assertIn("selected", label)
        self.assertIn("highlighted", label)

    def test_interaction_summary_label_none(self):
        """interaction_summary_label(None) returns fallback."""
        *_, _, interactive, _, _, _ = self._import_modules()
        self.assertEqual(
            interactive.interaction_summary_label(None), "No interactive state"
        )

    # ── Rule 17: count_active_interactions ──────────────────────────

    def test_count_active_interactions(self):
        """count_active_interactions tallies states."""
        *_, _, interactive, _, _, _ = self._import_modules()

        items = (
            interactive.InteractiveVisualComponent(
                component_id="a",
                interaction=interactive.ComponentInteractionState(state_label="SELECTED"),
            ),
            interactive.InteractiveVisualComponent(
                component_id="b",
                interaction=interactive.ComponentInteractionState(state_label="NORMAL"),
            ),
            interactive.InteractiveVisualComponent(
                component_id="c",
                interaction=interactive.ComponentInteractionState(state_label="SELECTED"),
            ),
        )
        counts = interactive.count_active_interactions(items)
        self.assertEqual(counts.get("SELECTED"), 2)
        self.assertEqual(counts.get("NORMAL"), 1)

    def test_count_active_interactions_empty(self):
        """count_active_interactions returns empty dict."""
        *_, _, interactive, _, _, _ = self._import_modules()
        self.assertEqual(interactive.count_active_interactions(()), {})


if __name__ == "__main__":
    unittest.main()
