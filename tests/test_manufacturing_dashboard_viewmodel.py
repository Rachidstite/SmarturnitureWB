import unittest

from validation.intelligence.manufacturing_dashboard_viewmodel import (
    ManufacturingDashboardViewModel,
)

from validation.intelligence.manufacturing_score import (
    ManufacturingScore,
)

from validation.intelligence.manufacturing_intelligence_report import (
    ManufacturingIntelligenceReport,
)


class TestManufacturingDashboardViewModel(
    unittest.TestCase
):

    def test_viewmodel_maps_report(self):

        report = ManufacturingIntelligenceReport(
            errors=[],
            warnings=[1, 2],
            recommendations=[1],
            optimizations=[],
            cost_impacts=[1, 2, 3],
            score=ManufacturingScore(
                score=92,
                grade="A",
                explanation="Good"
            ),
            can_export=True,
        )

        vm = (
            ManufacturingDashboardViewModel
            .from_report(report)
        )

        self.assertEqual(
            vm.score,
            92
        )

        self.assertEqual(
            vm.grade,
            "A"
        )

        self.assertEqual(
            vm.warning_count,
            2
        )

        self.assertEqual(
            vm.recommendation_count,
            1
        )

        self.assertEqual(
            vm.cost_impact_count,
            3
        )

        self.assertTrue(
            vm.can_export
        )


if __name__ == "__main__":
    unittest.main()
