import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from domain.anchors import AnchorCoordinate, EdgeRef, HardwarePlacement, MountFace


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
        part.makeCylinder = lambda *args: _FakeShape(args)
        sys.modules["Part"] = part


class _FakeShape:
    def __init__(self, args=()):
        self.args = args

    def cut(self, _other):
        return self


class _FakeObject:
    def __init__(self, name):
        self.Name = name
        self.Label = name
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


class _RecordingHardwareBuilder:
    def __init__(self):
        self.hinges = []

    def add_hinge(self, name, pos, group):
        self.hinges.append((name, pos, group))


class TestVisualHingeRenderingCharacterization(unittest.TestCase):

    def setUp(self):
        _install_freecad_stubs()

    def test_door_builder_uses_system32_positions_today(self):
        from builders import door_builder

        importlib.reload(door_builder)
        hw_builder = _RecordingHardwareBuilder()
        hw_group = _FakeGroup()

        with patch.object(
            door_builder.System32Engine,
            "hinge_positions",
            return_value=[11.0, 22.0, 33.0],
        ) as hinge_positions:
            door_builder.DoorBuilder.build(
                _FakeDocument(),
                _FakeGroup(),
                "CHARACTERIZE_DOOR",
                500.0,
                1800.0,
                10.0,
                20.0,
                30.0,
                SimpleNamespace(mdf_thickness=18.0),
                "Overlay",
                hw_builder=hw_builder,
                hw_group=hw_group,
            )

        hinge_positions.assert_called_once_with(1800.0)
        self.assertEqual(
            [pos[2] for _name, pos, _group in hw_builder.hinges],
            [41.0, 52.0, 63.0],
        )

    def test_existing_visual_hinge_count_remains_system32_count(self):
        from builders import door_builder
        from domain.system32 import System32Engine

        importlib.reload(door_builder)
        hw_builder = _RecordingHardwareBuilder()

        door_builder.DoorBuilder.build(
            _FakeDocument(),
            _FakeGroup(),
            "HINGE_COUNT_DOOR",
            500.0,
            1800.0,
            0.0,
            0.0,
            0.0,
            SimpleNamespace(mdf_thickness=18.0),
            "Overlay",
            hw_builder=hw_builder,
            hw_group=_FakeGroup(),
        )

        self.assertEqual(
            len(hw_builder.hinges),
            len(System32Engine.hinge_positions(1800.0)),
        )

    def test_supplied_hinge_offsets_should_override_system32_positions(self):
        from builders import door_builder

        importlib.reload(door_builder)
        hw_builder = _RecordingHardwareBuilder()

        door_builder.DoorBuilder.build(
            _FakeDocument(),
            _FakeGroup(),
            "HINGE_OVERRIDE_DOOR",
            500.0,
            1800.0,
            0.0,
            0.0,
            0.0,
            SimpleNamespace(mdf_thickness=18.0),
            "Overlay",
            hw_builder=hw_builder,
            hw_group=_FakeGroup(),
            hinge_offsets=[100.0, 633.3333333333334, 1166.6666666666667, 1700.0],
        )

        self.assertEqual(
            [pos[2] for _name, pos, _group in hw_builder.hinges],
            [100.0, 633.3333333333334, 1166.6666666666667, 1700.0],
        )

    def test_scene_renderer_should_map_hinge_placements_to_door_ids(self):
        from builders.hardware_builder import HardwareBuilder
        from core.material_manager import MaterialManager
        from scene_graph.renderer import SceneRenderer

        placement = HardwarePlacement(
            host_node_id="DOOR_A",
            target_node_id="DOOR_A",
            hardware_intent="INTENT_HINGE",
            anchor=AnchorCoordinate(
                MountFace.BACK,
                EdgeRef.BOTTOM,
                offset_x=22.0,
                offset_y=633.3333333333334,
            ),
        )
        renderer = SceneRenderer(
            _FakeDocument(),
            MaterialManager(),
            HardwareBuilder(_FakeDocument()),
            {"Hardware": _FakeGroup()},
            placements=[placement],
        )

        self.assertEqual(
            renderer.hinge_offsets_for("DOOR_A"),
            [633.3333333333334],
        )

    def test_geometry_renderer_is_not_part_of_hinge_rendering(self):
        from gui import renderer

        importlib.reload(renderer)
        source_names = renderer.GeometryRenderer.render.__code__.co_names

        self.assertNotIn("DoorBuilder", source_names)
        self.assertNotIn("HardwareBuilder", source_names)
        self.assertNotIn("add_hinge", source_names)


if __name__ == "__main__":
    unittest.main()
