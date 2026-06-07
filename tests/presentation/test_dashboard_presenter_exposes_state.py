import unittest

from validation.intelligence.manufacturing_dashboard_viewmodel import (
    ManufacturingDashboardViewModel,
)

from presentation.manufacturing_dashboard_presenter import (
    ManufacturingDashboardPresenter,
)


class TestDashboardPresenterExposesState(
    unittest.TestCase
):

    def test_present_returns_dashboard_state(self):

        vm = ManufacturingDashboardViewModel(
            score=97,
            grade="A+",
            warning_count=1,
            recommendation_count=2,
            cost_impact_count=3,
            can_export=True,
        )

        presenter = (
            ManufacturingDashboardPresenter()
        )

        presenter.present(vm)

        state = presenter.state

        self.assertEqual(97, state.score)
        self.assertEqual("A+", state.grade)
        self.assertTrue(state.can_export)


if __name__ == "__main__":
    unittest.main()
