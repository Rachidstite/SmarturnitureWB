import unittest

from domain.entities import (
    SceneNode,
    Identity
)

from domain.core_types import (
    NodeRole,
    MachiningOperation
)

from manufacturing.unified_operation_collector import \
    UnifiedOperationCollector


class FakeSceneGraph:

    def __init__(self):
        self.physical_nodes = []


class TestUnifiedOperationCollector(unittest.TestCase):

    def test_collect_modern_operations(self):

        node = SceneNode(
            identity=Identity("P1"),
            role=NodeRole.SIDE_PANEL,
            width=600,
            height=720,
            thickness=18,
            material="MDF",
            edge_bands={}
        )

        node.machining_ops.append(
            MachiningOperation(
                op_type="DRILL",
                diameter=8,
                depth=12,
                face="TOP",
                local_x=50,
                local_y=100
            )
        )

        graph = FakeSceneGraph()
        graph.physical_nodes.append(node)

        ops = (
            UnifiedOperationCollector
            .collect_modern(graph)
        )

        self.assertEqual(
            len(ops),
            1
        )

        self.assertEqual(
            ops[0].source,
            "modern-core"
        )


if __name__ == "__main__":
    unittest.main()
