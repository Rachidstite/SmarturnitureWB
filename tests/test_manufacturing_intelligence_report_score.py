import unittest

from validation.intelligence.manufacturing_score import (
    ManufacturingScore,
)

from validation.intelligence.manufacturing_intelligence_report import (
    ManufacturingIntelligenceReport,
)


class TestManufacturingIntelligenceReportScore(
    unittest.TestCase
):

    def test_score_field_exists(self):

        report = ManufacturingIntelligenceReport(
            errors=[],
            warnings=[],
            recommendations=[],
            optimizations=[],
            cost_impacts=[],
            score=ManufacturingScore(
                score=95,
                grade="A",
                explanation="good"
            ),
            can_export=True,
        )

        self.assertEqual(
            report.score.score,
            95
        )


if __name__ == "__main__":
    unittest.main()
