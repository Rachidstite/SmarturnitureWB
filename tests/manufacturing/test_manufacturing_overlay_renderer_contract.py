import unittest
from pathlib import Path


class TestManufacturingOverlayRendererContract(unittest.TestCase):

    def test_future_renderer_method_exists(self):
        from scene_graph.renderer import SceneRenderer

        self.assertTrue(
            hasattr(SceneRenderer, "build_manufacturing_overlays")
        )

    def test_future_empty_marker_list_returns_empty_list(self):
        from scene_graph.renderer import SceneRenderer

        overlays = SceneRenderer.build_manufacturing_overlays([])

        self.assertEqual(overlays, [])

    def test_future_groove_slot_marker_passes_through_unchanged(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker
        from scene_graph.renderer import SceneRenderer

        marker = ManufacturingMarker(
            operation_type="GROOVE",
            target_node_id="BACK_PANEL_1",
            visual_type="SLOT",
            start_x=10.0,
            start_y=20.0,
            width=4.0,
            depth=8.0,
            length=1982.0,
            face="BACK",
            metadata={"source_operation_type": "GROOVE"},
        )

        overlays = SceneRenderer.build_manufacturing_overlays([marker])

        self.assertEqual(overlays, [marker])

    def test_future_minifix_circle_marker_passes_through_unchanged(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker
        from scene_graph.renderer import SceneRenderer

        marker = ManufacturingMarker(
            operation_type="MINIFIX",
            target_node_id="NODE_A",
            visual_type="CIRCLE",
            start_x=11.0,
            start_y=21.0,
            width=5.0,
            depth=9.0,
            length=120.0,
            face="LEFT",
            metadata={"source_operation_type": "MINIFIX"},
        )

        overlays = SceneRenderer.build_manufacturing_overlays([marker])

        self.assertEqual(overlays, [marker])

    def test_future_unknown_annotation_marker_passes_through_unchanged(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker
        from scene_graph.renderer import SceneRenderer

        marker = ManufacturingMarker(
            operation_type="CUSTOM_SLOT",
            target_node_id="NODE_B",
            visual_type="ANNOTATION",
            start_x=1.0,
            start_y=2.0,
            width=3.0,
            depth=4.0,
            length=5.0,
            face="FRONT",
            metadata={"source_operation_type": "CUSTOM_SLOT"},
        )

        overlays = SceneRenderer.build_manufacturing_overlays([marker])

        self.assertEqual(overlays, [marker])

    @unittest.expectedFailure
    def test_renderer_source_guard(self):
        source = Path("scene_graph/renderer.py").read_text(encoding="utf-8")

        self.assertNotIn("BackPanelEngine", source)
        self.assertNotIn("requires_groove", source)
        self.assertNotIn("FreeCAD", source)
        self.assertNotIn("Part", source)

    def test_future_renderer_output_is_list_of_manufacturing_markers_or_compatible_descriptors(
        self,
    ):
        from scene_graph.manufacturing_marker import ManufacturingMarker
        from scene_graph.renderer import SceneRenderer

        marker = ManufacturingMarker(
            operation_type="GROOVE",
            target_node_id="BACK_PANEL_1",
            visual_type="SLOT",
            start_x=10.0,
            start_y=20.0,
            width=4.0,
            depth=8.0,
            length=1982.0,
            face="BACK",
            metadata={"source_operation_type": "GROOVE"},
        )

        overlays = SceneRenderer.build_manufacturing_overlays([marker])

        self.assertIsInstance(overlays, list)
        self.assertTrue(
            all(isinstance(item, ManufacturingMarker) for item in overlays)
        )


if __name__ == "__main__":
    unittest.main()
