import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from shared.roles import NodeRole


def _install_freecad_stubs():
    if "FreeCAD" not in sys.modules:
        freecad = types.ModuleType("FreeCAD")
        freecad.GuiUp = False
        freecad.Vector = lambda *args: args
        freecad.Rotation = lambda *args: ("Rotation", args)
        freecad.Placement = lambda *args: ("Placement", args)
        freecad.getDocument = lambda _name: (_ for _ in ()).throw(NameError())
        freecad.newDocument = lambda _name: _FakeDocument()
        sys.modules["FreeCAD"] = freecad

    if "Part" not in sys.modules:
        part = types.ModuleType("Part")
        part.makeBox = lambda *args: _FakeShape(args)
        sys.modules["Part"] = part


class _FakeShape:
    def __init__(self, args=()):
        self.args = args
        self.cut_calls = []
        self.translated_by = []

    def cut(self, other):
        self.cut_calls.append(other)
        return _FakeShape(("cut", self.args, other.args))

    def translate(self, vector):
        self.translated_by.append(tuple(vector))


class _FakeObject:
    def __init__(self, name):
        self.Name = name
        self.Label = name
        self.Shape = None
        self.Placement = None
        self.ViewObject = SimpleNamespace()

    def addProperty(self, *_args):
        return None


class _FakeGroup:
    def __init__(self):
        self.objects = []

    def addObject(self, obj):
        self.objects.append(obj)


class _FakeDocument:
    def __init__(self):
        self.Objects = []

    def addObject(self, _type_name, name):
        obj = _FakeGroup() if _type_name == "App::DocumentObjectGroup" else _FakeObject(name)
        self.Objects.append(obj)
        return obj

    def removeObject(self, _name):
        return None

    def recompute(self):
        return None


class TestSceneRendererPanelShapeProcessorContract(unittest.TestCase):
    def setUp(self):
        _install_freecad_stubs()
        import scene_graph.renderer as renderer

        importlib.reload(renderer)
        self.renderer = renderer

    def _make_renderer(self, panel_features=None):
        doc = _FakeDocument()
        groups = {}
        return self.renderer.SceneRenderer(
            doc,
            SimpleNamespace(),
            None,
            groups,
            panel_features=panel_features,
        ), doc

    def test_scene_renderer_without_features_renders_unchanged(self):
        renderer, doc = self._make_renderer()
        node = SimpleNamespace(
            identity=SimpleNamespace(key="BACK_PANEL_TEST"),
            role=NodeRole.BACK_PANEL,
            width=100.0,
            depth=3.0,
            height=200.0,
            thickness=3.0,
            x=0.0,
            y=0.0,
            z=0.0,
            group="Carcass",
        )

        renderer._render_simple_panel(node)

        panel_obj = next(obj for obj in doc.Objects if isinstance(obj, _FakeObject))
        self.assertEqual(panel_obj.Shape.args, (100.0, 3.0, 200.0))
        self.assertEqual(panel_obj.Shape.cut_calls, [])

    def test_back_panel_groove_calls_process_panel_shape_and_assigns_result(self):
        renderer, doc = self._make_renderer(
            [
                SimpleNamespace(
                    kind="back_panel_groove",
                    node_id="BACK_PANEL_TEST",
                    placement=(4.0, 1.0, 4.0),
                    size=(112.0, 2.0, 2.0),
                    name="BACK_PANEL_TEST_Groove_Slot",
                )
            ]
        )
        node = SimpleNamespace(
            identity=SimpleNamespace(key="BACK_PANEL_TEST"),
            role=NodeRole.BACK_PANEL,
            width=100.0,
            depth=3.0,
            height=200.0,
            thickness=3.0,
            x=0.0,
            y=0.0,
            z=0.0,
            group="Carcass",
        )

        with patch.object(
            self.renderer,
            "process_panel_shape",
            side_effect=lambda base_shape, panel_node, panel_features, panel_origin=None: _FakeShape(
                ("processed", base_shape.args)
            ),
        ) as processor_spy:
            renderer._render_simple_panel(node)

        processor_spy.assert_called_once()
        called_base_shape, called_node, called_features = processor_spy.call_args.args[:3]
        self.assertEqual(called_base_shape.args, (100.0, 3.0, 200.0))
        self.assertEqual(called_node.identity.key, "BACK_PANEL_TEST")
        self.assertEqual(len(called_features), 1)
        self.assertEqual(
            processor_spy.call_args.kwargs["panel_origin"],
            (0.0, 0.0, 0.0),
        )

        panel_obj = next(obj for obj in doc.Objects if isinstance(obj, _FakeObject))
        self.assertEqual(panel_obj.Shape.args, ("processed", (100.0, 3.0, 200.0)))

    def test_unsupported_features_do_not_alter_shape(self):
        renderer, doc = self._make_renderer(
            [
                SimpleNamespace(
                    kind="hinge_cup_hole",
                    node_id="BACK_PANEL_TEST",
                    placement=(4.0, 1.0, 4.0),
                    size=(35.0, 3.0, 35.0),
                    name="BACK_PANEL_TEST_Hinge_Cup",
                )
            ]
        )
        node = SimpleNamespace(
            identity=SimpleNamespace(key="BACK_PANEL_TEST"),
            role=NodeRole.BACK_PANEL,
            width=100.0,
            depth=3.0,
            height=200.0,
            thickness=3.0,
            x=0.0,
            y=0.0,
            z=0.0,
            group="Carcass",
        )

        renderer._render_simple_panel(node)

        panel_obj = next(obj for obj in doc.Objects if isinstance(obj, _FakeObject))
        self.assertEqual(panel_obj.Shape.args, (100.0, 3.0, 200.0))
        self.assertEqual(panel_obj.Shape.cut_calls, [])

    def test_side_panel_with_shelf_pin_feature_uses_existing_processor_path(self):
        renderer, doc = self._make_renderer(
            [
                SimpleNamespace(
                    kind="shelf_pin_hole",
                    node_id="SIDE_PANEL_TEST",
                    placement=(2.0, 300.0, 64.0),
                    size=(5.0, 5.0, 5.0),
                    name="SIDE_PANEL_TEST_Shelf_Pin",
                )
            ]
        )
        node = SimpleNamespace(
            identity=SimpleNamespace(key="SIDE_PANEL_TEST"),
            role=NodeRole.SIDE_PANEL,
            width=18.0,
            depth=600.0,
            height=1982.0,
            thickness=18.0,
            x=0.0,
            y=0.0,
            z=0.0,
            group="Carcass",
        )

        with patch.object(
            self.renderer,
            "process_panel_shape",
            side_effect=lambda base_shape, panel_node, panel_features, panel_origin=None: _FakeShape(
                ("processed", base_shape.args)
            ),
        ) as processor_spy:
            renderer._render_simple_panel(node)

        processor_spy.assert_called_once()
        panel_obj = next(obj for obj in doc.Objects if isinstance(obj, _FakeObject))
        self.assertEqual(panel_obj.Shape.args, ("processed", (18.0, 600.0, 1982.0)))

    def test_side_panel_with_drawer_slide_feature_uses_existing_processor_path(self):
        renderer, doc = self._make_renderer(
            [
                SimpleNamespace(
                    kind="drawer_slide_line",
                    node_id="SIDE_PANEL_TEST",
                    placement=(2.0, 300.0, 64.0),
                    size=(5.0, 5.0, 5.0),
                    name="SIDE_PANEL_TEST_Drawer_Slide",
                )
            ]
        )
        node = SimpleNamespace(
            identity=SimpleNamespace(key="SIDE_PANEL_TEST"),
            role=NodeRole.SIDE_PANEL,
            width=18.0,
            depth=600.0,
            height=1982.0,
            thickness=18.0,
            x=0.0,
            y=0.0,
            z=0.0,
            group="Carcass",
        )

        with patch.object(
            self.renderer,
            "process_panel_shape",
            side_effect=lambda base_shape, panel_node, panel_features, panel_origin=None: _FakeShape(
                ("processed", base_shape.args)
            ),
        ) as processor_spy:
            renderer._render_simple_panel(node)

        processor_spy.assert_called_once()
        panel_obj = next(obj for obj in doc.Objects if isinstance(obj, _FakeObject))
        self.assertEqual(panel_obj.Shape.args, ("processed", (18.0, 600.0, 1982.0)))

    def test_top_panel_with_minifix_feature_uses_existing_processor_path(self):
        renderer, doc = self._make_renderer(
            [
                SimpleNamespace(
                    kind="minifix_hole",
                    node_id="TOP_PANEL_TEST",
                    placement=(34.0, 580.0, 0.0),
                    size=(15.0, 14.0, 15.0),
                    name="TOP_PANEL_TEST_Minifix_Drill",
                )
            ]
        )
        node = SimpleNamespace(
            identity=SimpleNamespace(key="TOP_PANEL_TEST"),
            role=NodeRole.TOP_PANEL,
            width=18.0,
            depth=600.0,
            height=1982.0,
            thickness=18.0,
            x=0.0,
            y=0.0,
            z=0.0,
            group="Carcass",
        )

        with patch.object(
            self.renderer,
            "process_panel_shape",
            side_effect=lambda base_shape, panel_node, panel_features, panel_origin=None: _FakeShape(
                ("processed", base_shape.args)
            ),
        ) as processor_spy:
            renderer._render_simple_panel(node)

        processor_spy.assert_called_once()
        panel_obj = next(obj for obj in doc.Objects if isinstance(obj, _FakeObject))
        self.assertEqual(panel_obj.Shape.args, ("processed", (18.0, 600.0, 1982.0)))

    def test_bottom_panel_with_confirmat_feature_uses_existing_processor_path(self):
        renderer, doc = self._make_renderer(
            [
                SimpleNamespace(
                    kind="confirmat_hole",
                    node_id="BOTTOM_PANEL_TEST",
                    placement=(0.0, 50.0, 0.0),
                    size=(7.0, 18.0, 7.0),
                    name="BOTTOM_PANEL_TEST_Confirmat_Drill",
                )
            ]
        )
        node = SimpleNamespace(
            identity=SimpleNamespace(key="BOTTOM_PANEL_TEST"),
            role=NodeRole.BOTTOM_PANEL,
            width=18.0,
            depth=600.0,
            height=1982.0,
            thickness=18.0,
            x=0.0,
            y=0.0,
            z=0.0,
            group="Carcass",
        )

        with patch.object(
            self.renderer,
            "process_panel_shape",
            side_effect=lambda base_shape, panel_node, panel_features, panel_origin=None: _FakeShape(
                ("processed", base_shape.args)
            ),
        ) as processor_spy:
            renderer._render_simple_panel(node)

        processor_spy.assert_called_once()
        panel_obj = next(obj for obj in doc.Objects if isinstance(obj, _FakeObject))
        self.assertEqual(panel_obj.Shape.args, ("processed", (18.0, 600.0, 1982.0)))

    def test_door_panel_with_hinge_feature_uses_existing_processor_path(self):
        renderer, doc = self._make_renderer(
            [
                SimpleNamespace(
                    kind="hinge_cup_hole",
                    node_id="DOOR_PANEL_TEST",
                    placement=(22.5, 1.5, 633.3333333333334),
                    size=(35.0, 3.0, 35.0),
                    name="DOOR_PANEL_TEST_Hinge_Cup",
                )
            ]
        )
        renderer.mat.mdf_thickness = 18.0
        node = SimpleNamespace(
            identity=SimpleNamespace(key="DOOR_PANEL_TEST"),
            role=NodeRole.DOOR_PANEL,
            width=500.0,
            depth=18.0,
            height=1800.0,
            thickness=18.0,
            x=0.0,
            y=0.0,
            z=0.0,
            group="Doors",
            metadata=SimpleNamespace(
                door_type="OVERLAY",
                cnc_enabled=False,
                hinge_side="LEFT",
                layer=0,
            ),
        )

        with patch.object(
            self.renderer,
            "process_panel_shape",
            side_effect=lambda base_shape, panel_node, panel_features, panel_origin=None: _FakeShape(
                ("processed", base_shape.args)
            ),
        ) as processor_spy:
            self.renderer._door_strategy(node, renderer)

        processor_spy.assert_called_once()
        panel_obj = next(
            obj for obj in doc.Objects
            if isinstance(obj, _FakeObject) and obj.Name == "DOOR_PANEL_TEST"
        )
        self.assertEqual(panel_obj.Shape.args, ("processed", (500.0, 18.0, 1800.0)))

    def test_non_back_panel_unsupported_features_preserve_shape(self):
        renderer, doc = self._make_renderer(
            [
                SimpleNamespace(
                    kind="back_panel_groove",
                    node_id="SIDE_PANEL_TEST",
                    placement=(4.0, 1.0, 4.0),
                    size=(112.0, 2.0, 2.0),
                    name="SIDE_PANEL_TEST_Groove_Slot",
                )
            ]
        )
        node = SimpleNamespace(
            identity=SimpleNamespace(key="SIDE_PANEL_TEST"),
            role=NodeRole.SIDE_PANEL,
            width=18.0,
            depth=600.0,
            height=1982.0,
            thickness=18.0,
            x=0.0,
            y=0.0,
            z=0.0,
            group="Carcass",
        )

        renderer._render_simple_panel(node)

        panel_obj = next(obj for obj in doc.Objects if isinstance(obj, _FakeObject))
        self.assertEqual(panel_obj.Shape.args, (18.0, 600.0, 1982.0))
        self.assertEqual(panel_obj.Shape.cut_calls, [])


if __name__ == "__main__":
    unittest.main()
