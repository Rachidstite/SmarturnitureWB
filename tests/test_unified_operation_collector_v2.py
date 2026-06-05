import unittest

from domain.builders import WardrobeBuilder

from manufacturing.unified_operation_collector import \
    UnifiedOperationCollector


class TestUnifiedOperationCollectorV2(unittest.TestCase):

    def test_collect_legacy_operations(self):

        project = WardrobeBuilder(
            uid="TEST",
            width=800,
            height=800,
            depth=400
        ).build()

        ops = (
            UnifiedOperationCollector
            .collect_legacy(project.graph)
        )

        self.assertEqual(
            len(ops),
            8
        )


if __name__ == "__main__":
    unittest.main()
