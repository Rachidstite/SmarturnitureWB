import unittest
from pathlib import Path
from types import SimpleNamespace


class TestManufacturingMarkerBuilderContract(unittest.TestCase):

    def test_future_marker_builder_exists_as_contract(self):
        import scene_graph.manufacturing_marker_builder as module

        self.assertTrue(hasattr(module, "ManufacturingMarkerBuilder"))

    def test_future_groove_maps_to_slot_marker(self):
        from domain.manufacturing_ops import Groove
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )

        node = SimpleNamespace(identity=SimpleNamespace(key="BACK_PANEL_1"))
        markers = ManufacturingMarkerBuilder.build(
            node=node,
            operations=[
                Groove(
                    start_x=10.0,
                    start_y=20.0,
                    width=4.0,
                    depth=8.0,
                    length=1982.0,
                    face="BACK",
                )
            ],
        )

        self.assertEqual(len(markers), 1)
        self.assertEqual(markers[0].visual_type, "SLOT")

    def test_future_minifix_maps_to_circle_marker(self):
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )

        node = SimpleNamespace(identity=SimpleNamespace(key="MINIFIX_NODE"))
        operation = SimpleNamespace(
            operation_type="MINIFIX",
            start_x=11.0,
            start_y=21.0,
            width=5.0,
            depth=9.0,
            length=120.0,
            face="LEFT",
        )

        markers = ManufacturingMarkerBuilder.build(node=node, operations=[operation])

        self.assertEqual(markers[0].visual_type, "CIRCLE")

    def test_future_confirmat_maps_to_circle_marker(self):
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )

        node = SimpleNamespace(identity=SimpleNamespace(key="CONFIRMAT_NODE"))
        operation = SimpleNamespace(
            operation_type="CONFIRMAT",
            start_x=12.0,
            start_y=22.0,
            width=6.0,
            depth=10.0,
            length=140.0,
            face="RIGHT",
        )

        markers = ManufacturingMarkerBuilder.build(node=node, operations=[operation])

        self.assertEqual(markers[0].visual_type, "CIRCLE")

    def test_future_dowel_maps_to_circle_marker(self):
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )

        node = SimpleNamespace(identity=SimpleNamespace(key="DOWEL_NODE"))
        operation = SimpleNamespace(
            operation_type="DOWEL",
            start_x=13.0,
            start_y=23.0,
            width=7.0,
            depth=11.0,
            length=160.0,
            face="TOP",
        )

        markers = ManufacturingMarkerBuilder.build(node=node, operations=[operation])

        self.assertEqual(markers[0].visual_type, "CIRCLE")

    def test_future_shelf_pin_maps_to_point_marker(self):
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )

        node = SimpleNamespace(identity=SimpleNamespace(key="SHELF_PIN_NODE"))
        operation = SimpleNamespace(
            operation_type="SHELF_PIN",
            start_x=14.0,
            start_y=24.0,
            width=8.0,
            depth=12.0,
            length=180.0,
            face="BOTTOM",
        )

        markers = ManufacturingMarkerBuilder.build(node=node, operations=[operation])

        self.assertEqual(markers[0].visual_type, "POINT")

    def test_future_unknown_operation_maps_to_annotation(self):
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )

        node = SimpleNamespace(identity=SimpleNamespace(key="UNKNOWN_NODE"))
        operation = SimpleNamespace(
            operation_type="CUSTOM_SLOT",
            start_x=1.0,
            start_y=2.0,
            width=3.0,
            depth=4.0,
            length=5.0,
            face="FRONT",
        )

        markers = ManufacturingMarkerBuilder.build(node=node, operations=[operation])

        self.assertEqual(markers[0].visual_type, "ANNOTATION")

    def test_future_empty_operation_list_returns_empty_marker_list(self):
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )

        node = SimpleNamespace(identity=SimpleNamespace(key="EMPTY_NODE"))

        markers = ManufacturingMarkerBuilder.build(node=node, operations=[])

        self.assertEqual(markers, [])

    def test_future_target_node_id_is_preserved(self):
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )

        node = SimpleNamespace(identity=SimpleNamespace(key="TARGET_NODE"))
        operation = SimpleNamespace(
            operation_type="GROOVE",
            start_x=10.0,
            start_y=20.0,
            width=4.0,
            depth=8.0,
            length=1982.0,
            face="BACK",
            metadata={"source_operation_type": "GROOVE"},
        )

        markers = ManufacturingMarkerBuilder.build(node=node, operations=[operation])

        self.assertEqual(markers[0].target_node_id, "TARGET_NODE")

    def test_future_metadata_is_preserved(self):
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )

        node = SimpleNamespace(identity=SimpleNamespace(key="META_NODE"))
        operation = SimpleNamespace(
            operation_type="GROOVE",
            start_x=10.0,
            start_y=20.0,
            width=4.0,
            depth=8.0,
            length=1982.0,
            face="BACK",
            metadata={"source_operation_type": "GROOVE", "host": "BACK_PANEL_1"},
        )

        markers = ManufacturingMarkerBuilder.build(node=node, operations=[operation])

        self.assertEqual(
            markers[0].metadata,
            {"source_operation_type": "GROOVE", "host": "BACK_PANEL_1"},
        )

    def test_builder_source_does_not_import_back_panel_engine_freecad_or_part(self):
        source = Path("scene_graph/manufacturing_marker_builder.py").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("BackPanelEngine", source)
        self.assertNotIn("FreeCAD", source)
        self.assertNotIn("Part", source)

    def test_future_builder_output_is_list_of_manufacturing_markers(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker
        from scene_graph.manufacturing_marker_builder import (
            ManufacturingMarkerBuilder,
        )

        node = SimpleNamespace(identity=SimpleNamespace(key="OUTPUT_NODE"))

        markers = ManufacturingMarkerBuilder.build(node=node, operations=[])

        self.assertIsInstance(markers, list)
        self.assertTrue(all(isinstance(marker, ManufacturingMarker) for marker in markers))


if __name__ == "__main__":
    unittest.main()
