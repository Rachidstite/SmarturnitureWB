import unittest
from unittest.mock import patch

from manufacturing.hybrid_extractor import \
    HybridManufacturingExtractor

from manufacturing.unified_manufacturing_operation import \
    UnifiedManufacturingOperation


class TestHybridExtractor(unittest.TestCase):

    @patch(
        "manufacturing.hybrid_extractor.UnifiedOperationCollector.collect_hybrid"
    )
    @patch(
        "manufacturing.hybrid_extractor.ManufacturingExtractor.extract"
    )
    def test_populates_unified_operations(
        self,
        mock_extract,
        mock_collect
    ):

        class FakeSpec:
            def __init__(self):
                self.unified_operations = []

        spec = FakeSpec()

        mock_extract.return_value = [spec]

        mock_collect.return_value = [
            UnifiedManufacturingOperation(
                operation_type="DRILL",
                source="modern-core"
            )
        ]

        result = (
            HybridManufacturingExtractor
            .extract(None)
        )

        self.assertEqual(
            len(result[0].unified_operations),
            1
        )

        self.assertEqual(
            result[0]
            .unified_operations[0]
            .operation_type,
            "DRILL"
        )


if __name__ == "__main__":
    unittest.main()
