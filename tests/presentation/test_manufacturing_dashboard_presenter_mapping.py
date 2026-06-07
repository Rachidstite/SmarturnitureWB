import unittest

from validation.intelligence.manufacturing_dashboard_viewmodel import (
    ManufacturingDashboardViewModel,
)

from presentation.manufacturing_dashboard_presenter import (
    ManufacturingDashboardPresenter,
)


class TestManufacturingDashboardPresenterMapping(
    unittest.TestCase
):

    def test_presenter_maps_viewmodel_to_state(self):

        vm = ManufacturingDashboardViewModel(
            score=95,
            grade="A+",
            warning_count=1,
            recommendation_count=2,
            cost_impact_count=3,
            can_export=True,
        )

        presenter = ManufacturingDashboardPresenter()

        presenter.present(vm)

        self.assertEqual(
            95,
            presenter.state.score,
        )

        self.assertEqual(
            "A+",
            presenter.state.grade,
        )


if __name__ == "__main__":
    unittest.main()
