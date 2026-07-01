import inspect
import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestVisualEngineeringMetadata(unittest.TestCase):
    def test_visual_metadata_contract_exists_and_is_safe(self):
        from scene_graph.metadata import (
            DrillHoleVisual,
            EdgeBandVisual,
            GrooveVisual,
            HardwareMarkerVisual,
            VisualMetadata,
        )

        for cls in (
            EdgeBandVisual,
            DrillHoleVisual,
            GrooveVisual,
            HardwareMarkerVisual,
            VisualMetadata,
        ):
            self.assertTrue(is_dataclass(cls))

        self.assertEqual(
            [field.name for field in fields(VisualMetadata)],
            [
                "edge_banding",
                "drill_holes",
                "grooves",
                "hardware_markers",
                "material_label",
                "finish_label",
            ],
        )

        metadata = VisualMetadata()
        self.assertEqual(metadata.edge_banding, ())
        self.assertEqual(metadata.drill_holes, ())
        self.assertEqual(metadata.grooves, ())
        self.assertEqual(metadata.hardware_markers, ())
        self.assertEqual(metadata.material_label, "")
        self.assertEqual(metadata.finish_label, "")

    def test_empty_metadata_does_not_break_renderer_resolution(self):
        from scene_graph.renderer import SceneRenderer

        node = SimpleNamespace(
            identity=SimpleNamespace(key="NODE-1"),
            material="MDF_18MM",
            edge_spec=None,
            edge_bandings="",
            metadata={},
        )

        metadata = SceneRenderer.resolve_visual_metadata(node)

        self.assertEqual(metadata.edge_banding, ())
        self.assertEqual(metadata.drill_holes, ())
        self.assertEqual(metadata.grooves, ())
        self.assertEqual(metadata.hardware_markers, ())
        self.assertEqual(metadata.material_label, "MDF_18MM")

    def test_edge_banding_metadata_can_be_carried(self):
        from manufacturing.edge_spec import EdgeSpec
        from scene_graph.renderer import SceneRenderer

        node = SimpleNamespace(
            identity=SimpleNamespace(key="SHELF-1"),
            material="MDF_18MM",
            edge_spec=EdgeSpec(top="ABS_1MM", right="PVC_2MM"),
            edge_bandings="",
            metadata={},
        )

        metadata = SceneRenderer.resolve_visual_metadata(node)

        self.assertEqual(
            [(item.side, item.banding) for item in metadata.edge_banding],
            [("TOP", "ABS_1MM"), ("RIGHT", "PVC_2MM")],
        )

    def test_drill_hole_markers_can_be_carried_from_cnc_evidence(self):
        from manufacturing.cnc_report import CNCReport, CNCReportRow
        from scene_graph.renderer import SceneRenderer

        node = SimpleNamespace(
            identity=SimpleNamespace(key="PANEL-1"),
            material="MDF_18MM",
            edge_spec=None,
            edge_bandings="",
            metadata={},
        )
        cnc_report = CNCReport(
            rows=[
                CNCReportRow(
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
                CNCReportRow(
                    panel_identity="PANEL-2",
                    operation_type="DRILL",
                    face="RIGHT",
                    x=1.0,
                    y=2.0,
                    z=3.0,
                    diameter=4.0,
                    depth=6.0,
                    axis="Y",
                    is_through=True,
                    source_operation_reference="op-2",
                ),
            ]
        )

        metadata = SceneRenderer.resolve_visual_metadata(node, cnc_report=cnc_report)

        self.assertEqual(len(metadata.drill_holes), 1)
        drill = metadata.drill_holes[0]
        self.assertEqual(drill.panel_identity, "PANEL-1")
        self.assertEqual(drill.face, "LEFT")
        self.assertEqual(drill.diameter, 5.0)
        self.assertEqual(drill.source_operation_reference, "op-1")

    def test_hardware_markers_can_be_carried_from_existing_hardware_evidence(self):
        from manufacturing.hardware_bom_report import HardwareBomReport, HardwareBomRow
        from scene_graph.renderer import SceneRenderer

        node = SimpleNamespace(
            identity=SimpleNamespace(key="door-01"),
            material="MDF_18MM",
            edge_spec=None,
            edge_bandings="",
            metadata={},
        )
        hardware_report = HardwareBomReport(
            bom_rows=[
                HardwareBomRow(
                    sku="HINGE_BLUM_110_V1",
                    description="Blum 110 degree hinge",
                    quantity=2,
                    component_reference=("door-01",),
                    cabinet_reference=("cabinet-01",),
                    hardware_category="HINGE",
                    source_operation_references=("op-1", "op-2"),
                )
            ]
        )

        metadata = SceneRenderer.resolve_visual_metadata(
            node,
            hardware_bom=hardware_report,
        )

        self.assertEqual(len(metadata.hardware_markers), 1)
        marker = metadata.hardware_markers[0]
        self.assertEqual(marker.panel_identity, "door-01")
        self.assertEqual(marker.sku, "HINGE_BLUM_110_V1")
        self.assertEqual(marker.quantity, 2)
        self.assertEqual(marker.hardware_category, "HINGE")

    def test_renderer_does_not_generate_manufacturing_evidence(self):
        from scene_graph.renderer import SceneRenderer

        source = inspect.getsource(SceneRenderer.resolve_visual_metadata)

        for token in (
            "CNCReportBuilder",
            "HardwareBomBuilder",
            "AssemblyPackageBuilder",
            "ManufacturingRuntimePipelineBuilder",
            "ManufacturingDecisionBuilder",
        ):
            self.assertNotIn(token, source)

    def test_renderer_visual_metadata_path_does_not_call_builders_or_validators(self):
        from scene_graph.renderer import SceneRenderer

        source = inspect.getsource(SceneRenderer.resolve_visual_metadata)

        self.assertNotIn("Builder", source)
        self.assertNotIn("Validator", source)
        self.assertNotIn(".build(", source)
        self.assertNotIn(".validate(", source)


if __name__ == "__main__":
    unittest.main()
