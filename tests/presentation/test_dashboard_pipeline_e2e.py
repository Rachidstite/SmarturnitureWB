import unittest

from validation.intelligence.manufacturing_dashboard_viewmodel import (
    ManufacturingDashboardViewModel,
)

from presentation.manufacturing_dashboard_presenter import (
    ManufacturingDashboardPresenter,
)


class TestDashboardPipelineE2E(
    unittest.TestCase
):

    def test_viewmodel_reaches_presenter_state(self):

        vm = ManufacturingDashboardViewModel(
            score=94,
            grade="A",
            warning_count=2,
            recommendation_count=3,
            cost_impact_count=1,
            can_export=True,
        )

        presenter = (
            ManufacturingDashboardPresenter()
        )

        state = presenter.present(
            vm
        )

        self.assertEqual(
            94,
            state.score,
        )

        self.assertEqual(
            "A",
            state.grade,
        )

        self.assertEqual(
            2,
            state.warning_count,
        )

        self.assertTrue(
            state.can_export
        )


if __name__ == "__main__":
    unittest.main()
