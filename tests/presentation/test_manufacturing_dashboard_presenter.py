import unittest

from presentation.manufacturing_dashboard_state import (
    ManufacturingDashboardState,
)

from presentation.manufacturing_dashboard_presenter import (
    ManufacturingDashboardPresenter,
)


class TestManufacturingDashboardPresenter(
    unittest.TestCase
):

    def test_presenter_stores_state(self):

        state = ManufacturingDashboardState(
            score=92,
            grade="A",
            warning_count=2,
            recommendation_count=1,
            cost_impact_count=3,
            can_export=True,
        )

        presenter = (
            ManufacturingDashboardPresenter()
        )

        presenter.set_state(
            state
        )

        self.assertIs(
            presenter.state,
            state
        )


if __name__ == "__main__":
    unittest.main()
