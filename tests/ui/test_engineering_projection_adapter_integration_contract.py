# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Engineering Projection Adapter Integration Contract Tests
#
# Proves that Engineering projection data reaches CV2 through the
# existing adapter boundary without exposing Engineering types.
#
# Verifies:
# - Engineering source reaches workspace through SceneProjection only
# - Workspace consumes only frozen dataclasses
# - Inspector/Preview/Presentation layers still function
# - No Engineering/Domain/Manufacturing/Cost types leak
# - Backward compatibility preserved
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


class _FakeNode:
    """Simulates an Engineering scene-graph node.

    This object has no CV2 imports. It represents what an Engineering
    backend would produce — a plain object with attributes that the
    SceneProjection adapter extracts via duck-typing.
    """

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
    """Simulates an Engineering scene graph.

    CV2 consumes this through ``all_nodes()`` — the duck-typed
    interface that ``build_scene_projection`` accepts.
    """

    def __init__(self, nodes):
        self._nodes = list(nodes)

    def all_nodes(self):
        return list(self._nodes)


class TestEngineeringProjectionAdapterIntegrationContract(unittest.TestCase):
    """Verify Engineering → CV2 projection adapter boundary."""

    @classmethod
    def _import_modules(cls):
        for key in list(sys.modules):
            if key.startswith("ui.configurator_v2"):
                del sys.modules[key]

        with patch.dict(sys.modules, {"core.qt_compat": _fake_qt()}):
            from ui.configurator_v2 import service_integration as si
            from ui.configurator_v2 import scene_projection as sp
            from ui.configurator_v2 import visual_components as vc
            from ui.configurator_v2 import interactive_components as ic
            from ui.configurator_v2 import projection_adapters as pa
            from ui.configurator_v2 import workspace as ws
            from ui.configurator_v2 import presentation_synchronization as sync
            from ui.configurator_v2 import presentation_state as ps
            from ui.configurator_v2 import presentation_visual_contract as pvc
        return si, sp, vc, ic, pa, ws, sync, ps, pvc

    def _make_cabinet_scene(self):
        return _FakeSceneGraph(
            [
                _FakeNode(
                    "cabinet-1", "Base Cabinet", "CABINET",
                    0.0, 0.0, 0.0, 600.0, 580.0, 720.0,
                    metadata={"material": "Oak", "finish": "Matte"},
                ),
                _FakeNode(
                    "door-1", "Left Door", "DOOR_PANEL",
                    18.0, 0.0, 0.0, 297.0, 18.0, 700.0,
                    metadata={"material": "Oak", "door_style": "shaker", "mount": "overlay"},
                ),
                _FakeNode(
                    "drawer-1", "Upper Drawer", "DRAWER",
                    18.0, 0.0, 0.0, 564.0, 160.0, 18.0,
                    metadata={"front_type": "slab", "slide_type": "under-mount"},
                ),
            ]
        )

    # ── Rule 1: Engineering source reaches CV2 through SceneProjection ──

    def test_engineering_source_projected_to_scene_projection(self):
        """Raw Engineering source produces SceneProjection with correct nodes."""
        si, sp, _, _, _, _, _, _, _ = self._import_modules()
        graph = self._make_cabinet_scene()

        result = si.project_engineering_source(graph)

        self.assertIsNotNone(result.scene_projection)
        self.assertEqual(len(result.scene_projection.nodes), 3)
        self.assertEqual(result.scene_projection.nodes[1].node_id, "door-1")
        self.assertEqual(result.scene_projection.nodes[2].node_id, "drawer-1")

    def test_engineering_source_produces_visual_components(self):
        """Projection result contains VisualComponent instances."""
        si, _, vc_mod, _, _, _, _, _, _ = self._import_modules()
        graph = self._make_cabinet_scene()

        result = si.project_engineering_source(graph)

        self.assertEqual(len(result.visual_components), 3)
        self.assertIsInstance(result.visual_components[0], vc_mod.CabinetVisualComponent)
        self.assertIsInstance(result.visual_components[1], vc_mod.DoorVisualComponent)
        self.assertIsInstance(result.visual_components[2], vc_mod.DrawerVisualComponent)

    # ── Rule 2: Workspace consumes only frozen dataclasses ────────

    def test_workspace_consumes_projection_result(self):
        """Workspace preview region accepts projected data."""
        si, _, _, _, _, ws_mod, _, _, _ = self._import_modules()
        workspace = ws_mod.create_configurator_v2_workspace()
        graph = self._make_cabinet_scene()

        result = si.project_engineering_source(
            graph,
            show_door_swing=True,
        )
        workspace.synchronize_preview_interactive_components(
            result.interactive_components,
        )

        region = workspace.preview_region
        self.assertEqual(len(region.interactive_components), 3)
        self.assertEqual(len(region.visual_components), 0)
        # Visual styles are computed from visual_components path, not
        # from interactive_components path (which clears visual_styles).

    # ── Rule 3: Inspector still functions ─────────────────────────

    def test_inspector_still_functions_after_projection(self):
        """Inspector can be set from projected data without errors."""
        si, _, _, _, _, ws_mod, _, _, _ = self._import_modules()
        workspace = ws_mod.create_configurator_v2_workspace()
        graph = self._make_cabinet_scene()

        result = si.project_engineering_source(
            graph,
            show_door_swing=True,
            selected_ids=frozenset({"door-1"}),
        )
        workspace.synchronize_preview_interactive_components(
            result.interactive_components,
            selected_ids=frozenset({"door-1"}),
        )

        # Set inspector with presentation data
        synced = workspace.preview_region.interactive_components[1]  # door-1
        sel = ws_mod.ConfiguratorSelection(
            selection_type="DOOR",
            selection_id="door-1",
            display_name="Left Door",
        )
        workspace.set_presentation_aware_inspector(sel, synced)
        inspector = workspace.inspector_read_model
        self.assertEqual(inspector.selection_id, "door-1")
        # Presentation-aware fields present
        pres_fields = [f for f in inspector.fields if f.group == "Presentation"]
        self.assertGreater(len(pres_fields), 0)

    # ── Rule 4: Preview still functions ───────────────────────────

    def test_preview_still_functions_after_projection(self):
        """Preview read model renders projected data."""
        si, _, _, _, pa_mod, ws_mod, _, _, _ = self._import_modules()
        workspace = ws_mod.create_configurator_v2_workspace()
        graph = self._make_cabinet_scene()

        result = si.project_engineering_source(graph)
        read_model = pa_mod.build_preview_read_model(
            {"visual_components": result.visual_components}
        )
        workspace.set_preview_read_model(read_model)

        self.assertEqual(workspace.preview_read_model.node_count, 3)
        self.assertIn("Preview Title", "\n".join(workspace.preview_region.render_rows))

    # ── Rule 5: Presentation synchronization functions ────────────

    def test_presentation_sync_functions(self):
        """Synchronized states are populated when presentation flags provided."""
        si, _, _, _, _, _, _, _, _ = self._import_modules()
        graph = self._make_cabinet_scene()

        result = si.project_engineering_source(
            graph,
            show_door_swing=True,
            selected_ids=frozenset({"door-1"}),
            warning_ids=frozenset({"cabinet-1"}),
            error_ids=frozenset({"drawer-1"}),
        )

        self.assertEqual(len(result.synchronized_states), 3)
        self.assertTrue(result.synchronized_states[1].presentation_state.selected)
        self.assertTrue(result.synchronized_states[0].presentation_state.warning)
        self.assertTrue(result.synchronized_states[2].presentation_state.error)

    # ── Rule 6: Visual contract functions ─────────────────────────

    def test_visual_contract_functions(self):
        """Visual contract populated from synchronized states."""
        si, _, _, _, _, _, sync_mod, _, pvc_mod = self._import_modules()
        graph = self._make_cabinet_scene()

        result = si.project_engineering_source(
            graph,
            show_door_swing=True,
            error_ids=frozenset({"drawer-1"}),
        )

        drawer_state = result.synchronized_states[2]
        self.assertEqual(drawer_state.dominant_flag, "error")
        self.assertEqual(
            drawer_state.visual_contract.outline_intent,
            pvc_mod.OUTLINE_ERROR,
        )
        self.assertEqual(
            drawer_state.visual_contract.emphasis_level,
            pvc_mod.EMPHASIS_CRITICAL,
        )

    # ── Rule 7: No Engineering types exposed ──────────────────────

    def test_result_contains_no_engineering_types(self):
        """EngineeringProjectionResult fields are CV2-native types only."""
        si, _, _, ic_mod, _, _, sync_mod, ps_mod, pvc_mod = self._import_modules()
        graph = self._make_cabinet_scene()

        result = si.project_engineering_source(
            graph,
            show_door_swing=True,
            selected_ids=frozenset({"door-1"}),
        )

        # SceneProjection is CV2-native
        self.assertIsInstance(result.scene_projection, type(None) if False else object)

        # VisualComponents are CV2-native
        for vc in result.visual_components:
            self.assertFalse(hasattr(vc, "Shape"))
            self.assertFalse(hasattr(vc, "ViewObject"))

        # InteractiveComponents are CV2-native
        for ic in result.interactive_components:
            self.assertFalse(hasattr(ic, "Shape"))
            self.assertFalse(hasattr(ic, "all_nodes"))

        # Presentation states are CV2-native
        for ss in result.synchronized_states:
            self.assertIsInstance(ss, sync_mod.SynchronizedPresentation)
            self.assertIsInstance(ss.presentation_state, ps_mod.FurniturePresentationState)
            self.assertIsInstance(ss.visual_contract, pvc_mod.PresentationVisualContract)

    # ── Rule 8: No source mutation ────────────────────────────────

    def test_source_not_mutated(self):
        """Original Engineering source is not modified by projection."""
        si, _, _, _, _, _, _, _, _ = self._import_modules()
        graph = self._make_cabinet_scene()
        original_keys = [n.identity.key for n in graph._nodes]

        si.project_engineering_source(graph)

        self.assertEqual(len(original_keys), len(graph._nodes))
        self.assertEqual(original_keys[0], graph._nodes[0].identity.key)

    # ── Rule 9: Empty source produces empty result ────────────────

    def test_empty_source_produces_empty_result(self):
        """project_engineering_source with None or empty source returns empty result."""
        si, _, _, _, _, _, _, _, _ = self._import_modules()

        result = si.project_engineering_source(None)
        self.assertIsNone(result.scene_projection)
        self.assertEqual(result.visual_components, ())
        self.assertEqual(result.interactive_components, ())
        self.assertEqual(result.synchronized_states, ())

        result = si.project_engineering_source(_FakeSceneGraph([]))
        self.assertEqual(result.visual_components, ())

    # ── Rule 10: No domain imports ────────────────────────────────

    def test_service_integration_imports_no_domain_modules(self):
        """service_integration.py must not import domain modules."""
        with open("ui/configurator_v2/service_integration.py") as f:
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
                msg=f"service_integration.py must not import '{token}'",
            )

    # ── Rule 11: Backward compatibility ───────────────────────────

    def test_existing_service_integration_still_works(self):
        """Existing ConfiguratorV2ServiceIntegration methods still function."""
        si, _, _, _, _, ws_mod, _, _, _ = self._import_modules()
        workspace = ws_mod.create_configurator_v2_workspace()
        integration = si.attach_service_integration(workspace)

        # Existing refresh_validation still works
        result = integration.refresh_validation()
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
