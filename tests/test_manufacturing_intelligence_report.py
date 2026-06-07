import unittest

from validation.intelligence.manufacturing_intelligence_report import (
    ManufacturingIntelligenceReport,
)


class TestManufacturingIntelligenceReport(
    unittest.TestCase
):

    def test_report_fields(self):

        report = ManufacturingIntelligenceReport(
            errors=[],
            warnings=[],
            recommendations=[],
            optimizations=[],
            can_export=True,
        )

        self.assertTrue(
            report.can_export
        )


if __name__ == "__main__":
    unittest.main()
