import unittest
from unittest.mock import patch

from manufacturing.unified_operation_collector import \
    UnifiedOperationCollector

from manufacturing.unified_manufacturing_operation import \
    UnifiedManufacturingOperation


class TestHybridOperationCollector(unittest.TestCase):

    @patch.object(
        UnifiedOperationCollector,
        "collect_legacy"
    )
    @patch.object(
        UnifiedOperationCollector,
        "collect_modern"
    )
    def test_collect_hybrid_merges_both_sources(
        self,
        mock_modern,
        mock_legacy
    ):

        mock_legacy.return_value = [
            UnifiedManufacturingOperation(
                operation_type="FACE_DRILL",
                source="legacy"
            )
        ]

        mock_modern.return_value = [
            UnifiedManufacturingOperation(
                operation_type="DRILL",
                source="modern-core"
            )
        ]

        result = (
            UnifiedOperationCollector
            .collect_hybrid(None)
        )

        self.assertEqual(
            len(result),
            2
        )

        self.assertEqual(
            result[0].source,
            "legacy"
        )

        self.assertEqual(
            result[1].source,
            "modern-core"
        )


if __name__ == "__main__":
    unittest.main()
