import unittest

from validation.intelligence.manufacturing_score_engine import (
    ManufacturingScoreEngine,
)

from validation.intelligence.manufacturing_intelligence_report import (
    ManufacturingIntelligenceReport,
)


class TestManufacturingScoreGrades(
    unittest.TestCase
):

    def test_perfect_report_gets_a_plus(self):

        report = ManufacturingIntelligenceReport(
            errors=[],
            warnings=[],
            recommendations=[],
            optimizations=[],
            cost_impacts=[],
            score=None,
            can_export=True,
        )

        result = (
            ManufacturingScoreEngine()
            .calculate(report)
        )

        self.assertEqual(
            result.grade,
            "A+"
        )


if __name__ == "__main__":
    unittest.main()
