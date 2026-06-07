import unittest

from validation.intelligence.manufacturing_score_engine import (
    ManufacturingScoreEngine,
)

from validation.intelligence.manufacturing_intelligence_report import (
    ManufacturingIntelligenceReport,
)


class TestManufacturingScoreCalculation(
    unittest.TestCase
):

    def test_perfect_report_scores_100(self):

        report = ManufacturingIntelligenceReport(
            errors=[],
            warnings=[],
            recommendations=[],
            optimizations=[],
            cost_impacts=[],
            can_export=True,
        )

        score = (
            ManufacturingScoreEngine()
            .calculate(report)
        )

        self.assertEqual(
            score.score,
            100
        )


if __name__ == "__main__":
    unittest.main()
