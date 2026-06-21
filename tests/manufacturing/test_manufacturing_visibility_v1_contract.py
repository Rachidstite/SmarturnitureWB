import unittest

from types import SimpleNamespace


class TestManufacturingVisibilityV1Contract(unittest.TestCase):

    def test_future_confirmat_marker_is_consumed_by_renderer(self):
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )
        from scene_graph.renderer import SceneRenderer

        node = SimpleNamespace(identity=SimpleNamespace(key="CONFIRMAT_NODE"))
        markers = ManufacturingMarkerBuilder.build(
            node=node,
            operations=[
                SimpleNamespace(
                    operation_type="CONFIRMAT",
                    start_x=12.0,
                    start_y=22.0,
                    width=6.0,
                    depth=10.0,
                    length=140.0,
                    face="RIGHT",
                    metadata={"source_operation_type": "CONFIRMAT"},
                )
            ],
        )

        self.assertEqual(len(markers), 1)
        self.assertEqual(markers[0].operation_type, "CONFIRMAT")
        self.assertEqual(markers[0].visual_type, "CIRCLE")

        overlays = SceneRenderer.build_manufacturing_overlays(markers)

        self.assertEqual(overlays, markers)

    def test_future_shelf_pin_marker_is_consumed_by_renderer(self):
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )
        from scene_graph.renderer import SceneRenderer

        node = SimpleNamespace(identity=SimpleNamespace(key="SHELF_PIN_NODE"))
        markers = ManufacturingMarkerBuilder.build(
            node=node,
            operations=[
                SimpleNamespace(
                    operation_type="SHELF_PIN",
                    start_x=14.0,
                    start_y=24.0,
                    width=8.0,
                    depth=12.0,
                    length=180.0,
                    face="BOTTOM",
                    metadata={"source_operation_type": "SHELF_PIN"},
                )
            ],
        )

        self.assertEqual(len(markers), 1)
        self.assertEqual(markers[0].operation_type, "SHELF_PIN")
        self.assertEqual(markers[0].visual_type, "POINT")

        overlays = SceneRenderer.build_manufacturing_overlays(markers)

        self.assertEqual(overlays, markers)

    def test_future_drawer_slide_marker_is_consumed_by_renderer(self):
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )
        from scene_graph.renderer import SceneRenderer

        node = SimpleNamespace(identity=SimpleNamespace(key="DRAWER_SLIDE_NODE"))
        markers = ManufacturingMarkerBuilder.build(
            node=node,
            operations=[
                SimpleNamespace(
                    operation_type="DRAWER_SLIDE",
                    start_x=32.0,
                    start_y=50.0,
                    width=3.0,
                    depth=12.0,
                    length=450.0,
                    face="LEFT",
                    metadata={"source_operation_type": "DRAWER_SLIDE"},
                )
            ],
        )

        self.assertEqual(len(markers), 1)
        self.assertEqual(markers[0].operation_type, "DRAWER_SLIDE")
        self.assertEqual(markers[0].visual_type, "ANNOTATION")

        overlays = SceneRenderer.build_manufacturing_overlays(markers)

        self.assertEqual(overlays, markers)


if __name__ == "__main__":
    unittest.main()
