import unittest

from validation.intelligence.manufacturing_dashboard_viewmodel import (
    ManufacturingDashboardViewModel,
)

from presentation.manufacturing_dashboard_presenter import (
    ManufacturingDashboardPresenter,
)


class TestManufacturingDashboardPresenterDisplay(
    unittest.TestCase
):

    def test_presenter_accepts_viewmodel(self):

        vm = ManufacturingDashboardViewModel(
            score=91,
            grade="A",
            warning_count=2,
            recommendation_count=3,
            cost_impact_count=1,
            can_export=True,
        )

        presenter = (
            ManufacturingDashboardPresenter()
        )

        presenter.present(vm)

        self.assertEqual(
            91,
            presenter.state.score,
        )

        self.assertEqual(
            "A",
            presenter.state.grade,
        )


if __name__ == "__main__":
    unittest.main()
