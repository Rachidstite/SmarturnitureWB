import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch


def _install_freecad_stubs():
    if "FreeCAD" not in sys.modules:
        freecad = types.ModuleType("FreeCAD")
        freecad.GuiUp = False
        freecad.Vector = lambda *args: args
        freecad.Rotation = lambda *args: ("Rotation", args)
        freecad.Placement = lambda *args: ("Placement", args)
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


class TestPanelShapeProcessorV1(unittest.TestCase):
    def setUp(self):
        _install_freecad_stubs()

    def test_back_panel_groove_is_cut_from_base_shape(self):
        import manufacturing.panel_shape_processor as panel_shape_processor

        base_shape = _FakeShape(("base",))
        panel = SimpleNamespace(identity=SimpleNamespace(key="BACK_PANEL_1"))
        features = [
            SimpleNamespace(
                kind="back_panel_groove",
                node_id="BACK_PANEL_1",
                placement=(4.0, 1.0, 4.0),
                size=(112.0, 2.0, 2.0),
                name="BACK_PANEL_1_Groove_Slot",
            ),
            SimpleNamespace(
                kind="shelf_pin_hole",
                node_id="BACK_PANEL_1",
                placement=(10.0, 10.0, 10.0),
                size=(5.0, 5.0, 5.0),
                name="BACK_PANEL_1_Shelf_Pin",
            ),
        ]

        with patch.object(
            panel_shape_processor,
            "Part",
            SimpleNamespace(makeBox=lambda *args: _FakeShape(args)),
        ):
            result = panel_shape_processor.process_panel_shape(
                base_shape,
                panel,
                features,
                panel_origin=(0.0, 0.0, 0.0),
            )

        self.assertIsNot(result, base_shape)
        self.assertEqual(len(base_shape.cut_calls), 1)
        self.assertEqual(base_shape.cut_calls[0].args, (112.0, 2.0, 2.0))
        self.assertEqual(base_shape.cut_calls[0].translated_by, [(4.0, 1.0, 4.0)])

    def test_supported_shelf_pin_feature_is_cut_from_base_shape(self):
        import manufacturing.panel_shape_processor as panel_shape_processor

        base_shape = _FakeShape(("base",))
        panel = SimpleNamespace(identity=SimpleNamespace(key="SIDE_PANEL_1"))
        features = [
            SimpleNamespace(
                kind="shelf_pin_hole",
                node_id="SIDE_PANEL_1",
                placement=(2.0, 300.0, 64.0),
                size=(5.0, 5.0, 5.0),
                name="SIDE_PANEL_1_Shelf_Pin",
            ),
        ]

        with patch.object(
            panel_shape_processor,
            "Part",
            SimpleNamespace(makeBox=lambda *args: _FakeShape(args)),
        ):
            result = panel_shape_processor.process_panel_shape(
                base_shape,
                panel,
                features,
                panel_origin=(0.0, 0.0, 0.0),
            )

        self.assertIsNot(result, base_shape)
        self.assertEqual(len(base_shape.cut_calls), 1)
        self.assertEqual(base_shape.cut_calls[0].args, (5.0, 5.0, 5.0))
        self.assertEqual(base_shape.cut_calls[0].translated_by, [(2.0, 300.0, 64.0)])

    def test_supported_drawer_slide_feature_is_cut_from_base_shape(self):
        import manufacturing.panel_shape_processor as panel_shape_processor

        base_shape = _FakeShape(("base",))
        panel = SimpleNamespace(identity=SimpleNamespace(key="SIDE_PANEL_1"))
        features = [
            SimpleNamespace(
                kind="drawer_slide_line",
                node_id="SIDE_PANEL_1",
                placement=(2.0, 300.0, 64.0),
                size=(5.0, 5.0, 5.0),
                name="SIDE_PANEL_1_Drawer_Slide",
            ),
        ]

        with patch.object(
            panel_shape_processor,
            "Part",
            SimpleNamespace(makeBox=lambda *args: _FakeShape(args)),
        ):
            result = panel_shape_processor.process_panel_shape(
                base_shape,
                panel,
                features,
                panel_origin=(0.0, 0.0, 0.0),
            )

        self.assertIsNot(result, base_shape)
        self.assertEqual(len(base_shape.cut_calls), 1)
        self.assertEqual(base_shape.cut_calls[0].args, (5.0, 5.0, 5.0))
        self.assertEqual(base_shape.cut_calls[0].translated_by, [(2.0, 300.0, 64.0)])

    def test_supported_minifix_feature_is_cut_from_base_shape(self):
        import manufacturing.panel_shape_processor as panel_shape_processor

        base_shape = _FakeShape(("base",))
        panel = SimpleNamespace(identity=SimpleNamespace(key="TOP_PANEL_1"))
        features = [
            SimpleNamespace(
                kind="minifix_hole",
                node_id="TOP_PANEL_1",
                placement=(34.0, 580.0, 0.0),
                size=(15.0, 14.0, 15.0),
                name="TOP_PANEL_1_Minifix_Drill",
            ),
        ]

        with patch.object(
            panel_shape_processor,
            "Part",
            SimpleNamespace(makeBox=lambda *args: _FakeShape(args)),
        ):
            result = panel_shape_processor.process_panel_shape(
                base_shape,
                panel,
                features,
                panel_origin=(0.0, 0.0, 0.0),
            )

        self.assertIsNot(result, base_shape)
        self.assertEqual(len(base_shape.cut_calls), 1)
        self.assertEqual(base_shape.cut_calls[0].args, (15.0, 14.0, 15.0))
        self.assertEqual(base_shape.cut_calls[0].translated_by, [(34.0, 580.0, 0.0)])

    def test_supported_confirmat_feature_is_cut_from_base_shape(self):
        import manufacturing.panel_shape_processor as panel_shape_processor

        base_shape = _FakeShape(("base",))
        panel = SimpleNamespace(identity=SimpleNamespace(key="DIVIDER_1"))
        features = [
            SimpleNamespace(
                kind="confirmat_hole",
                node_id="DIVIDER_1",
                placement=(0.0, 50.0, 0.0),
                size=(7.0, 18.0, 7.0),
                name="DIVIDER_1_Confirmat_Drill",
            ),
        ]

        with patch.object(
            panel_shape_processor,
            "Part",
            SimpleNamespace(makeBox=lambda *args: _FakeShape(args)),
        ):
            result = panel_shape_processor.process_panel_shape(
                base_shape,
                panel,
                features,
                panel_origin=(0.0, 0.0, 0.0),
            )

        self.assertIsNot(result, base_shape)
        self.assertEqual(len(base_shape.cut_calls), 1)
        self.assertEqual(base_shape.cut_calls[0].args, (7.0, 18.0, 7.0))
        self.assertEqual(base_shape.cut_calls[0].translated_by, [(0.0, 50.0, 0.0)])

    def test_edge_banding_features_are_pass_through_and_do_not_cut_geometry(self):
        from manufacturing.panel_shape_processor import process_panel_shape

        base_shape = _FakeShape(("base",))
        panel = SimpleNamespace(identity=SimpleNamespace(key="DOOR_PANEL_1"))
        features = [
            SimpleNamespace(
                kind="edge_banding_strip",
                node_id="DOOR_PANEL_1",
                placement=(0.0, 0.0, 0.0),
                size=(10.0, 1.0, 20.0),
                name="DOOR_PANEL_1_Edge_Banding",
            ),
        ]

        result = process_panel_shape(
            base_shape,
            panel,
            features,
            panel_origin=(0.0, 0.0, 0.0),
        )

        self.assertIs(result, base_shape)
        self.assertEqual(base_shape.cut_calls, [])

    def test_supported_hinge_feature_is_cut_from_base_shape(self):
        import manufacturing.panel_shape_processor as panel_shape_processor

        base_shape = _FakeShape(("base",))
        panel = SimpleNamespace(identity=SimpleNamespace(key="DOOR_PANEL_1"))
        features = [
            SimpleNamespace(
                kind="hinge_cup_hole",
                node_id="DOOR_PANEL_1",
                placement=(22.5, 1.5, 633.3333333333334),
                size=(35.0, 3.0, 35.0),
                name="DOOR_PANEL_1_Hinge_Cup",
            ),
        ]

        with patch.object(
            panel_shape_processor,
            "Part",
            SimpleNamespace(makeBox=lambda *args: _FakeShape(args)),
        ):
            result = panel_shape_processor.process_panel_shape(
                base_shape,
                panel,
                features,
                panel_origin=(0.0, 0.0, 0.0),
            )

        self.assertIsNot(result, base_shape)
        self.assertEqual(len(base_shape.cut_calls), 1)
        self.assertEqual(base_shape.cut_calls[0].args, (35.0, 3.0, 35.0))
        self.assertEqual(base_shape.cut_calls[0].translated_by, [(22.5, 1.5, 633.3333333333334)])

    def test_unsupported_feature_kinds_are_ignored(self):
        from manufacturing.panel_shape_processor import process_panel_shape

        base_shape = _FakeShape(("base",))
        panel = SimpleNamespace(identity=SimpleNamespace(key="BACK_PANEL_1"))
        features = [
            SimpleNamespace(
                kind="hinge_cup_hole",
                node_id="BACK_PANEL_1",
                placement=(4.0, 1.0, 4.0),
                size=(112.0, 2.0, 2.0),
                name="BACK_PANEL_1_Hinge_Cup",
            ),
            SimpleNamespace(
                kind="drawer_slide_line",
                node_id="BACK_PANEL_1",
                placement=(8.0, 2.0, 3.0),
                size=(10.0, 2.0, 2.0),
                name="BACK_PANEL_1_Drawer_Slide",
            ),
        ]

        result = process_panel_shape(
            base_shape,
            panel,
            features,
            panel_origin=(0.0, 0.0, 0.0),
        )

        self.assertIs(result, base_shape)
        self.assertEqual(base_shape.cut_calls, [])

    def test_cut_failure_preserves_original_shape_and_logs_warning(self):
        from manufacturing.panel_shape_processor import process_panel_shape

        class _ExplodingShape(_FakeShape):
            def cut(self, _other):
                raise RuntimeError("boom")

        base_shape = _ExplodingShape(("base",))
        panel = SimpleNamespace(identity=SimpleNamespace(key="BACK_PANEL_1"))
        features = [
            SimpleNamespace(
                kind="back_panel_groove",
                node_id="BACK_PANEL_1",
                placement=(4.0, 1.0, 4.0),
                size=(112.0, 2.0, 2.0),
                name="BACK_PANEL_1_Groove_Slot",
            )
        ]

        with patch("manufacturing.panel_shape_processor.logger.warning") as warning_spy:
            result = process_panel_shape(
                base_shape,
                panel,
                features,
                panel_origin=(0.0, 0.0, 0.0),
            )

        self.assertIs(result, base_shape)
        warning_spy.assert_called()


if __name__ == "__main__":
    unittest.main()
