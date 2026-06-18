import unittest

from domain.builders import Identity, SceneGraph, SceneNode
from domain.core_types import MachiningOperation, NodeCategory, NodeRole
from manufacturing.extractor import ManufacturingExtractor


class TestManufacturingExtractorNodeMachiningContract(unittest.TestCase):

    def test_extractor_includes_existing_node_machining_ops_in_panel_spec(self):
        graph = SceneGraph()
        panel = SceneNode(
            identity=Identity("PANEL_WITH_NODE_OPS"),
            role=NodeRole.SIDE_PANEL,
            width=400.0,
            height=720.0,
            thickness=18.0,
            material="MDF_18_WHITE",
            category=NodeCategory.PHYSICAL,
        )
        operation = MachiningOperation(
            op_type="DRILL",
            face="LEFT",
            local_x=32.0,
            local_y=50.0,
            diameter=5.0,
            depth=12.0,
            axis="Z",
            is_through=False,
        )
        panel.machining_ops.append(operation)
        graph.add_node(panel)

        specs = ManufacturingExtractor.extract(graph)

        by_id = {spec.identity: spec for spec in specs}
        self.assertIn("PANEL_WITH_NODE_OPS", by_id)
        self.assertIn(operation, by_id["PANEL_WITH_NODE_OPS"].cnc_operations)


if __name__ == "__main__":
    unittest.main()
