import unittest

from validation.intelligence.manufacturing_score_engine import (
    ManufacturingScoreEngine,
)

from validation.intelligence.manufacturing_intelligence_report import (
    ManufacturingIntelligenceReport,
)


class TestManufacturingScorePenalties(
    unittest.TestCase
):

    def test_error_reduces_score(self):

        report = ManufacturingIntelligenceReport(
            errors=[object()],
            warnings=[],
            recommendations=[],
            optimizations=[],
            cost_impacts=[],
            can_export=False,
        )

        score = (
            ManufacturingScoreEngine()
            .calculate(report)
        )

        self.assertLess(
            score.score,
            100
        )

    def test_warning_reduces_score(self):

        report = ManufacturingIntelligenceReport(
            errors=[],
            warnings=[object()],
            recommendations=[],
            optimizations=[],
            cost_impacts=[],
            can_export=True,
        )

        score = (
            ManufacturingScoreEngine()
            .calculate(report)
        )

        self.assertLess(
            score.score,
            100
        )


if __name__ == "__main__":
    unittest.main()
