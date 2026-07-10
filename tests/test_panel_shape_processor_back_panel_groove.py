import unittest
from types import SimpleNamespace
from unittest.mock import patch


class _FakeToolShape:
    def __init__(self, args=()):
        self.args = args
        self.translated_by = []

    def translate(self, vector):
        self.translated_by.append(tuple(vector))


class _FakePanelShape:
    def __init__(self, cuts=None):
        self.cuts = list(cuts or [])

    def cut(self, other):
        return _FakePanelShape(self.cuts + [other])


class TestPanelShapeProcessorBackPanelGroove(unittest.TestCase):
    def setUp(self):
        import manufacturing.panel_shape_processor as panel_shape_processor

        self.module = panel_shape_processor

    def _install_part_stub(self):
        return patch.object(
            self.module,
            "Part",
            SimpleNamespace(makeBox=lambda *args: _FakeToolShape(args)),
        )

    def test_no_groove_returns_identical_shape(self):
        from manufacturing.panel_shape_processor import process_panel_shape

        base_shape = _FakePanelShape()
        panel = SimpleNamespace(identity=SimpleNamespace(key="BACK_PANEL_1"))
        features = [
            SimpleNamespace(
                kind="hinge_cup_hole",
                node_id="BACK_PANEL_1",
                placement=(10.0, 20.0, 30.0),
                size=(5.0, 5.0, 5.0),
                name="BACK_PANEL_1_Hinge_Cup",
            )
        ]

        with self._install_part_stub():
            result = process_panel_shape(
                base_shape,
                panel,
                features,
                panel_origin=(0.0, 0.0, 0.0),
            )

        self.assertIs(result, base_shape)
        self.assertEqual(result.cuts, [])

    def test_one_groove_returns_modified_shape(self):
        from manufacturing.panel_shape_processor import process_panel_shape

        base_shape = _FakePanelShape()
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

        with self._install_part_stub():
            result = process_panel_shape(
                base_shape,
                panel,
                features,
                panel_origin=(0.0, 0.0, 0.0),
            )

        self.assertIsNot(result, base_shape)
        self.assertEqual(len(result.cuts), 1)
        self.assertEqual(result.cuts[0].args, (112.0, 2.0, 2.0))
        self.assertEqual(result.cuts[0].translated_by, [(4.0, 1.0, 4.0)])

    def test_multiple_grooves_are_all_applied(self):
        from manufacturing.panel_shape_processor import process_panel_shape

        base_shape = _FakePanelShape()
        panel = SimpleNamespace(identity=SimpleNamespace(key="BACK_PANEL_1"))
        features = [
            SimpleNamespace(
                kind="back_panel_groove",
                node_id="BACK_PANEL_1",
                placement=(4.0, 1.0, 4.0),
                size=(112.0, 2.0, 2.0),
                name="BACK_PANEL_1_Groove_Left",
            ),
            SimpleNamespace(
                kind="shelf_pin_hole",
                node_id="BACK_PANEL_1",
                placement=(10.0, 10.0, 10.0),
                size=(5.0, 5.0, 5.0),
                name="BACK_PANEL_1_Shelf_Pin",
            ),
            SimpleNamespace(
                kind="back_panel_groove",
                node_id="BACK_PANEL_1",
                placement=(8.0, 2.0, 4.0),
                size=(112.0, 2.0, 2.0),
                name="BACK_PANEL_1_Groove_Right",
            ),
        ]

        with self._install_part_stub():
            result = process_panel_shape(
                base_shape,
                panel,
                features,
                panel_origin=(0.0, 0.0, 0.0),
            )

        self.assertEqual(len(result.cuts), 2)
        self.assertEqual(result.cuts[0].args, (112.0, 2.0, 2.0))
        self.assertEqual(result.cuts[0].translated_by, [(4.0, 1.0, 4.0)])
        self.assertEqual(result.cuts[1].args, (112.0, 2.0, 2.0))
        self.assertEqual(result.cuts[1].translated_by, [(8.0, 2.0, 4.0)])

    def test_side_panel_back_panel_groove_is_cut_from_base_shape(self):
        from manufacturing.panel_shape_processor import process_panel_shape

        base_shape = _FakePanelShape()
        panel = SimpleNamespace(
            identity=SimpleNamespace(key="SIDE_PANEL_1"),
            role=SimpleNamespace(value="SIDE_PANEL"),
        )
        features = [
            SimpleNamespace(
                kind="back_panel_groove",
                node_id="SIDE_PANEL_1",
                placement=(10.0, 577.0, 18.0),
                size=(8.0, 3.2, 684.0),
                name="SIDE_PANEL_1_Back_Groove",
            )
        ]

        with self._install_part_stub():
            result = process_panel_shape(
                base_shape,
                panel,
                features,
                panel_origin=(0.0, 0.0, 0.0),
            )

        self.assertIsNot(result, base_shape)
        self.assertEqual(len(result.cuts), 1)
        self.assertEqual(result.cuts[0].args, (8.0, 3.2, 684.0))
        self.assertEqual(result.cuts[0].translated_by, [(10.0, 577.0, 18.0)])


if __name__ == "__main__":
    unittest.main()
