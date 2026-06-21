import unittest
from pathlib import Path
from types import SimpleNamespace


class TestManufacturingVisualizationContract(unittest.TestCase):

    def test_scene_renderer_source_does_not_reference_back_panel_engine(self):
        source = Path("scene_graph/renderer.py").read_text(encoding="utf-8")

        self.assertNotIn("BackPanelEngine", source)
        self.assertNotIn("requires_groove", source)

    @unittest.expectedFailure
    def test_future_groove_operation_can_be_converted_to_visual_marker_contract(self):
        from domain.manufacturing_ops import Groove
        from scene_graph.renderer import SceneRenderer

        operation = Groove(
            start_x=10.0,
            start_y=20.0,
            width=4.0,
            depth=8.0,
            length=1982.0,
            face="BACK",
        )
        node = SimpleNamespace(
            identity=SimpleNamespace(key="BACK_PANEL_TEST"),
            metadata=SimpleNamespace(
                section_index=0,
                groove_depth=8.0,
                back_offset=20.0,
                extends_into_groove=True,
            ),
        )

        markers = SceneRenderer.build_manufacturing_markers(
            node,
            operations=[operation],
        )

        self.assertEqual(len(markers), 1)
        marker = markers[0]
        self.assertEqual(marker["operation_type"], "GROOVE")
        self.assertEqual(marker["start_x"], 10.0)
        self.assertEqual(marker["start_y"], 20.0)
        self.assertEqual(marker["width"], 4.0)
        self.assertEqual(marker["depth"], 8.0)
        self.assertEqual(marker["length"], 1982.0)
        self.assertEqual(marker["face"], "BACK")
        self.assertEqual(marker["target_node_id"], "BACK_PANEL_TEST")

    @unittest.expectedFailure
    def test_future_manufacturing_marker_contract_is_generic_across_operation_types(self):
        from scene_graph.renderer import SceneRenderer

        node = SimpleNamespace(
            identity=SimpleNamespace(key="MARKER_GENERIC_NODE"),
            metadata=SimpleNamespace(section_index=1),
        )
        operations = [
            SimpleNamespace(
                operation_type="GROOVE",
                start_x=10.0,
                start_y=20.0,
                width=4.0,
                depth=8.0,
                length=1982.0,
                face="BACK",
            ),
            SimpleNamespace(
                operation_type="MINIFIX",
                start_x=11.0,
                start_y=21.0,
                width=5.0,
                depth=9.0,
                length=120.0,
                face="LEFT",
            ),
            SimpleNamespace(
                operation_type="CONFIRMAT",
                start_x=12.0,
                start_y=22.0,
                width=6.0,
                depth=10.0,
                length=140.0,
                face="RIGHT",
            ),
            SimpleNamespace(
                operation_type="DOWEL",
                start_x=13.0,
                start_y=23.0,
                width=7.0,
                depth=11.0,
                length=160.0,
                face="TOP",
            ),
            SimpleNamespace(
                operation_type="SHELF_PIN",
                start_x=14.0,
                start_y=24.0,
                width=8.0,
                depth=12.0,
                length=180.0,
                face="BOTTOM",
            ),
        ]

        markers = SceneRenderer.build_manufacturing_markers(
            node,
            operations=operations,
        )

        self.assertEqual(
            [marker["operation_type"] for marker in markers],
            [
                "GROOVE",
                "MINIFIX",
                "CONFIRMAT",
                "DOWEL",
                "SHELF_PIN",
            ],
        )
        self.assertEqual(
            [marker["target_node_id"] for marker in markers],
            ["MARKER_GENERIC_NODE"] * 5,
        )

    @unittest.expectedFailure
    def test_future_no_manufacturing_operations_produce_no_markers(self):
        from scene_graph.renderer import SceneRenderer

        node = SimpleNamespace(
            identity=SimpleNamespace(key="EMPTY_NODE"),
            metadata=SimpleNamespace(section_index=2),
        )

        markers = SceneRenderer.build_manufacturing_markers(
            node,
            operations=[],
        )

        self.assertEqual(markers, [])


if __name__ == "__main__":
    unittest.main()
