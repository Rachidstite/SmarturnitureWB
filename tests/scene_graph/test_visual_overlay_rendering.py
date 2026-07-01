import inspect
import unittest


class TestVisualOverlayRendering(unittest.TestCase):
    def test_empty_metadata_renders_safely(self):
        from scene_graph.metadata import VisualMetadata
        from scene_graph.renderer import SceneRenderer

        overlays = SceneRenderer.build_visual_overlays(VisualMetadata())

        self.assertEqual(overlays, [])

    def test_edge_overlays_render_from_metadata(self):
        from scene_graph.metadata import EdgeBandVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        overlays = SceneRenderer.build_visual_overlays(
            VisualMetadata(
                edge_banding=(
                    EdgeBandVisual(side="TOP", banding="ABS_1MM", label="TOP edge: ABS_1MM"),
                    EdgeBandVisual(side="RIGHT", banding="PVC_2MM", label="RIGHT edge: PVC_2MM"),
                )
            )
        )

        self.assertEqual(
            overlays,
            [
                {
                    "overlay_type": "edge_banding",
                    "visual_type": "EDGE_MARKER",
                    "side": "TOP",
                    "banding": "ABS_1MM",
                    "label": "TOP edge: ABS_1MM",
                },
                {
                    "overlay_type": "edge_banding",
                    "visual_type": "EDGE_MARKER",
                    "side": "RIGHT",
                    "banding": "PVC_2MM",
                    "label": "RIGHT edge: PVC_2MM",
                },
            ],
        )

    def test_drill_overlays_render_from_metadata(self):
        from scene_graph.metadata import DrillHoleVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        overlays = SceneRenderer.build_visual_overlays(
            VisualMetadata(
                drill_holes=(
                    DrillHoleVisual(
                        panel_identity="PANEL-1",
                        operation_type="DRILL",
                        face="LEFT",
                        x=10.0,
                        y=20.0,
                        z=30.0,
                        diameter=5.0,
                        depth=12.0,
                        axis="X",
                        is_through=False,
                        source_operation_reference="op-1",
                    ),
                )
            )
        )

        self.assertEqual(len(overlays), 1)
        self.assertEqual(overlays[0]["overlay_type"], "drill_hole")
        self.assertEqual(overlays[0]["visual_type"], "CIRCLE")
        self.assertEqual(overlays[0]["panel_identity"], "PANEL-1")
        self.assertEqual(overlays[0]["diameter"], 5.0)
        self.assertEqual(overlays[0]["source_operation_reference"], "op-1")

    def test_hardware_markers_render_from_metadata(self):
        from scene_graph.metadata import HardwareMarkerVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        overlays = SceneRenderer.build_visual_overlays(
            VisualMetadata(
                hardware_markers=(
                    HardwareMarkerVisual(
                        panel_identity="door-01",
                        sku="HINGE_BLUM_110_V1",
                        quantity=2,
                        hardware_category="HINGE",
                        label="Blum 110 degree hinge",
                        component_reference=("door-01",),
                        cabinet_reference=("cabinet-01",),
                        source_operation_references=("op-1", "op-2"),
                    ),
                    HardwareMarkerVisual(
                        panel_identity="drawer-01",
                        sku="DRAWER_SLIDE_STANDARD_450",
                        quantity=2,
                        hardware_category="DRAWER_SLIDE",
                        label="450mm standard drawer slide",
                        component_reference=("drawer-01",),
                        cabinet_reference=("cabinet-01",),
                        source_operation_references=("op-3",),
                    ),
                    HardwareMarkerVisual(
                        panel_identity="side-01",
                        sku="SHELF_PIN_5MM",
                        quantity=4,
                        hardware_category="SHELF_PIN",
                        label="Shelf pin 5mm",
                        component_reference=("side-01",),
                        cabinet_reference=("cabinet-01",),
                        source_operation_references=("op-4",),
                    ),
                )
            )
        )

        self.assertEqual(
            [overlay["visual_type"] for overlay in overlays],
            ["HINGE_SYMBOL", "DRAWER_SLIDE_SYMBOL", "SHELF_PIN_SYMBOL"],
        )

    def test_grooves_render_from_metadata(self):
        from scene_graph.metadata import GrooveVisual, VisualMetadata
        from scene_graph.renderer import SceneRenderer

        overlays = SceneRenderer.build_visual_overlays(
            VisualMetadata(
                grooves=(
                    GrooveVisual(
                        panel_identity="BACK-1",
                        face="BACK",
                        depth=8.0,
                        label="Back panel groove",
                        source_rule="BackPanelRule:GROOVE",
                    ),
                )
            )
        )

        self.assertEqual(len(overlays), 1)
        self.assertEqual(overlays[0]["overlay_type"], "groove")
        self.assertEqual(overlays[0]["visual_type"], "CENTERLINE")
        self.assertEqual(overlays[0]["source_rule"], "BackPanelRule:GROOVE")

    def test_renderer_overlay_path_has_no_manufacturing_builder_dependency(self):
        from scene_graph.renderer import SceneRenderer

        source = inspect.getsource(SceneRenderer.build_visual_overlays)
        helper_source = inspect.getsource(SceneRenderer._hardware_marker_overlays)

        for token in (
            "CNCReportBuilder",
            "HardwareBomBuilder",
            "AssemblyPackageBuilder",
            "ManufacturingRuntimePipelineBuilder",
            "ManufacturingDecisionBuilder",
        ):
            self.assertNotIn(token, source)
            self.assertNotIn(token, helper_source)


if __name__ == "__main__":
    unittest.main()
