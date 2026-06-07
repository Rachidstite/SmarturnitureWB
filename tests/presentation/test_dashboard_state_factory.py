import unittest

from validation.intelligence.manufacturing_dashboard_viewmodel import (
    ManufacturingDashboardViewModel,
)

from presentation.manufacturing_dashboard_state import (
    ManufacturingDashboardState,
)


class TestDashboardStateFactory(unittest.TestCase):

    def test_state_created_from_viewmodel(self):

        vm = ManufacturingDashboardViewModel(
            score=92,
            grade="A",
            warning_count=2,
            recommendation_count=1,
            cost_impact_count=3,
            can_export=True,
        )

        state = ManufacturingDashboardState.from_viewmodel(
            vm
        )

        self.assertEqual(92, state.score)
        self.assertEqual("A", state.grade)
        self.assertEqual(2, state.warning_count)
        self.assertEqual(1, state.recommendation_count)
        self.assertEqual(3, state.cost_impact_count)
        self.assertTrue(state.can_export)


if __name__ == "__main__":
    unittest.main()
