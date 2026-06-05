import unittest
from unittest.mock import patch

from exports.hybrid_manufacturing_report import \
    HybridManufacturingReportEngine

from manufacturing.unified_manufacturing_operation import \
    UnifiedManufacturingOperation


class FakeSpec:

    def __init__(self):

        self.identity = "P1"

        self.unified_operations = [
            UnifiedManufacturingOperation(
                operation_type="DRILL",
                diameter=8,
                depth=12,
                source="modern-core"
            )
        ]


class TestHybridManufacturingReport(unittest.TestCase):

    @patch(
        "exports.hybrid_manufacturing_report.HybridManufacturingExtractor.extract"
    )
    def test_generates_report_from_unified_operations(
        self,
        mock_extract
    ):

        mock_extract.return_value = [
            FakeSpec()
        ]

        report = (
            HybridManufacturingReportEngine
            .generate(None)
        )

        self.assertEqual(
            len(report.lines),
            1
        )

        self.assertEqual(
            report.lines[0].operation_type,
            "DRILL"
        )


if __name__ == "__main__":
    unittest.main()
