import unittest

from validation.intelligence.manufacturing_score import (
    ManufacturingScore,
)

from validation.intelligence.manufacturing_intelligence_report import (
    ManufacturingIntelligenceReport,
)

from validation.intelligence.manufacturing_intelligence_csv_report import (
    ManufacturingIntelligenceCSVReport,
)


class TestManufacturingIntelligenceCSVReport(
    unittest.TestCase
):

    def test_report_contains_score(self):

        report = ManufacturingIntelligenceReport(
            errors=[],
            warnings=[],
            recommendations=[],
            optimizations=[],
            cost_impacts=[],
            score=ManufacturingScore(
                score=92,
                grade="A",
                explanation="good"
            ),
            can_export=True,
        )

        rows = (
            ManufacturingIntelligenceCSVReport()
            .build(report)
        )

        self.assertGreater(
            len(rows),
            0
        )


if __name__ == "__main__":
    unittest.main()
