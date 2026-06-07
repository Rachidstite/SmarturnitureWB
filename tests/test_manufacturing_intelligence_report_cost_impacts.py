import unittest

from validation.intelligence.manufacturing_intelligence_report import (
    ManufacturingIntelligenceReport,
)


class TestManufacturingIntelligenceReportCostImpacts(
    unittest.TestCase
):

    def test_cost_impacts_field_exists(self):

        report = ManufacturingIntelligenceReport(
            errors=[],
            warnings=[],
            recommendations=[],
            optimizations=[],
            cost_impacts=[],
            can_export=True,
        )

        self.assertEqual(
            len(report.cost_impacts),
            0
        )


if __name__ == "__main__":
    unittest.main()
