import inspect
import unittest


class TestViewportOverlayRendering(unittest.TestCase):
    def test_empty_overlays_return_empty_commands(self):
        from scene_graph.renderer import SceneRenderer

        self.assertEqual(SceneRenderer.build_viewport_overlay_commands([]), [])

    def test_edge_overlay_creates_viewport_ready_command(self):
        from scene_graph.renderer import SceneRenderer

        commands = SceneRenderer.build_viewport_overlay_commands(
            [
                {
                    "overlay_type": "edge_banding",
                    "visual_type": "EDGE_MARKER",
                    "side": "TOP",
                    "banding": "ABS_1MM",
                    "label": "TOP edge: ABS_1MM",
                }
            ]
        )

        self.assertEqual(
            commands,
            [
                {
                    "command_type": "edge_marker",
                    "overlay_type": "edge_banding",
                    "label": "TOP edge: ABS_1MM",
                    "side": "TOP",
                    "banding": "ABS_1MM",
                    "position": None,
                    "face": "",
                    "source_reference": "",
                }
            ],
        )

    def test_drill_overlay_creates_circle_command_from_existing_coordinates(self):
        from scene_graph.renderer import SceneRenderer

        commands = SceneRenderer.build_viewport_overlay_commands(
            [
                {
                    "overlay_type": "drill_hole",
                    "visual_type": "CIRCLE",
                    "panel_identity": "PANEL-1",
                    "face": "LEFT",
                    "x": 10.0,
                    "y": 20.0,
                    "z": 30.0,
                    "diameter": 5.0,
                    "depth": 12.0,
                    "axis": "X",
                    "is_through": False,
                    "source_operation_reference": "op-1",
                }
            ]
        )

        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["command_type"], "circle_marker")
        self.assertEqual(commands[0]["position"], (10.0, 20.0, 30.0))
        self.assertEqual(commands[0]["diameter"], 5.0)
        self.assertEqual(commands[0]["source_reference"], "op-1")

    def test_groove_overlay_creates_centerline_command_only_when_data_exists(self):
        from scene_graph.renderer import SceneRenderer

        commands = SceneRenderer.build_viewport_overlay_commands(
            [
                {
                    "overlay_type": "groove",
                    "visual_type": "CENTERLINE",
                    "panel_identity": "BACK-1",
                    "face": "BACK",
                    "depth": 8.0,
                    "label": "Back panel groove",
                    "source_rule": "BackPanelRule:GROOVE",
                },
                {
                    "overlay_type": "groove",
                    "visual_type": "CENTERLINE",
                    "panel_identity": "BACK-2",
                    "face": "",
                    "depth": 0.0,
                    "label": "",
                    "source_rule": "",
                },
            ]
        )

        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["command_type"], "centerline_marker")
        self.assertEqual(commands[0]["face"], "BACK")
        self.assertEqual(commands[0]["source_reference"], "BackPanelRule:GROOVE")

    def test_hardware_marker_creates_symbolic_command(self):
        from scene_graph.renderer import SceneRenderer

        commands = SceneRenderer.build_viewport_overlay_commands(
            [
                {
                    "overlay_type": "hardware_marker",
                    "visual_type": "HINGE_SYMBOL",
                    "panel_identity": "door-01",
                    "sku": "HINGE_BLUM_110_V1",
                    "quantity": 2,
                    "hardware_category": "HINGE",
                    "label": "Blum 110 degree hinge",
                    "component_reference": ("door-01",),
                    "cabinet_reference": ("cabinet-01",),
                    "source_operation_references": ("op-1", "op-2"),
                }
            ]
        )

        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["command_type"], "symbolic_marker")
        self.assertEqual(commands[0]["symbol"], "HINGE_SYMBOL")
        self.assertEqual(commands[0]["size"], 2)
        self.assertEqual(commands[0]["source_reference"], ("op-1", "op-2"))

    def test_renderer_does_not_call_manufacturing_builders(self):
        from scene_graph.renderer import SceneRenderer

        source = inspect.getsource(SceneRenderer.build_viewport_overlay_commands)
        helper_source = inspect.getsource(SceneRenderer._drill_viewport_command)

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
