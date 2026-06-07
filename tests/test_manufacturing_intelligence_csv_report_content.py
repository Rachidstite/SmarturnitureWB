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


class TestManufacturingIntelligenceCSVReportContent(
    unittest.TestCase
):

    def test_score_and_grade_rows_exist(self):

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

        self.assertIn(
            ["Manufacturing Score", 92],
            rows
        )

        self.assertIn(
            ["Grade", "A"],
            rows
        )


if __name__ == "__main__":
    unittest.main()
