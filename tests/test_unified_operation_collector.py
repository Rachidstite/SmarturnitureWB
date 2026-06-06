import unittest
from types import SimpleNamespace

from domain.core_types import MachiningOperation
from manufacturing.unified_operation_collector import UnifiedOperationCollector


class TestUnifiedOperationCollector(unittest.TestCase):

    def test_modern_operations_preserve_panel_ownership(self):
        node = SimpleNamespace(
            identity=SimpleNamespace(key="PANEL_A"),
            machining_ops=[
                MachiningOperation(
                    op_type="DRILL",
                    diameter=5,
                    depth=12,
                    face="TOP",
                    local_x=10,
                    local_y=20,
                )
            ],
        )

        scene_graph = SimpleNamespace(
            physical_nodes=[node]
        )

        operations = UnifiedOperationCollector.collect_modern(scene_graph)

        self.assertEqual(len(operations), 1)
        self.assertEqual(
            operations[0].metadata.get("panel_id"),
            "PANEL_A"
        )


if __name__ == "__main__":
    unittest.main()
