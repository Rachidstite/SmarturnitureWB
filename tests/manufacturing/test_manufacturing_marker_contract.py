import unittest
from dataclasses import fields


class TestManufacturingMarkerContract(unittest.TestCase):

    def test_manufacturing_marker_is_a_frozen_dataclass(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker

        self.assertTrue(getattr(ManufacturingMarker, "__dataclass_params__").frozen)

    def test_field_order_is_stable(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker

        self.assertEqual(
            [field.name for field in fields(ManufacturingMarker)],
            [
                "operation_type",
                "target_node_id",
                "visual_type",
                "start_x",
                "start_y",
                "width",
                "depth",
                "length",
                "face",
                "metadata",
            ],
        )

    def test_defaults_are_safe(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker

        marker = ManufacturingMarker()

        self.assertEqual(marker.operation_type, "")
        self.assertEqual(marker.target_node_id, "")
        self.assertEqual(marker.visual_type, "")
        self.assertEqual(marker.start_x, 0.0)
        self.assertEqual(marker.start_y, 0.0)
        self.assertEqual(marker.width, 0.0)
        self.assertEqual(marker.depth, 0.0)
        self.assertEqual(marker.length, 0.0)
        self.assertEqual(marker.face, "")
        self.assertEqual(marker.metadata, {})

    def test_metadata_uses_default_factory_and_is_not_shared(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker

        first_marker = ManufacturingMarker()
        second_marker = ManufacturingMarker()

        first_marker.metadata["sample"] = "value"

        self.assertEqual(second_marker.metadata, {})
        self.assertIsNot(first_marker.metadata, second_marker.metadata)

    def test_can_represent_groove_marker(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker

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

        self.assertEqual(marker.operation_type, "GROOVE")
        self.assertEqual(marker.target_node_id, "BACK_PANEL_1")
        self.assertEqual(marker.visual_type, "SLOT")
        self.assertEqual(marker.start_x, 10.0)
        self.assertEqual(marker.start_y, 20.0)
        self.assertEqual(marker.width, 4.0)
        self.assertEqual(marker.depth, 8.0)
        self.assertEqual(marker.length, 1982.0)
        self.assertEqual(marker.face, "BACK")
        self.assertEqual(marker.metadata["source_operation_type"], "GROOVE")

    def test_can_represent_generic_operation_types(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker

        operations = [
            ManufacturingMarker(operation_type="MINIFIX", target_node_id="NODE_A"),
            ManufacturingMarker(operation_type="CONFIRMAT", target_node_id="NODE_B"),
            ManufacturingMarker(operation_type="DOWEL", target_node_id="NODE_C"),
            ManufacturingMarker(operation_type="SHELF_PIN", target_node_id="NODE_D"),
        ]

        self.assertEqual(
            [marker.operation_type for marker in operations],
            ["MINIFIX", "CONFIRMAT", "DOWEL", "SHELF_PIN"],
        )

    def test_contains_no_freecad_specific_fields(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker

        marker_field_names = {field.name for field in fields(ManufacturingMarker)}
        forbidden_fields = {
            "world_position",
            "world_transform",
            "placement",
            "shape",
            "document_object",
        }

        self.assertTrue(forbidden_fields.isdisjoint(marker_field_names))

    def test_contains_no_manufacturing_rule_fields(self):
        from scene_graph.manufacturing_marker import ManufacturingMarker

        marker_field_names = {field.name for field in fields(ManufacturingMarker)}
        forbidden_fields = {
            "requires_groove",
            "thickness_rule",
            "eligibility",
            "rule_engine",
        }

        self.assertTrue(forbidden_fields.isdisjoint(marker_field_names))


if __name__ == "__main__":
    unittest.main()
