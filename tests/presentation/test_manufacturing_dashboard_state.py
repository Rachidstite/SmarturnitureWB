import unittest

from presentation.manufacturing_dashboard_state import (
    ManufacturingDashboardState,
)


class ManufacturingDashboardStateTests(unittest.TestCase):

    def test_state_can_be_created(self):
        state = ManufacturingDashboardState(
            score=92,
            grade="A+",
            warning_count=3,
            recommendation_count=4,
            cost_impact_count=2,
            can_export=True,
        )

        self.assertEqual(92, state.score)
        self.assertEqual("A+", state.grade)
        self.assertEqual(3, state.warning_count)
        self.assertEqual(4, state.recommendation_count)
        self.assertEqual(2, state.cost_impact_count)
        self.assertTrue(state.can_export)


if __name__ == "__main__":
    unittest.main()
