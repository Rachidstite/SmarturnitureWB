import unittest


class TestDashboardWidgetContract(
    unittest.TestCase
):

    def test_widget_exposes_update_state(self):

        with open(
            "ui/manufacturing_dashboard_widget.py",
            "r",
            encoding="utf-8",
        ) as f:
            source = f.read()

        self.assertIn(
            "def update_state",
            source,
        )

        self.assertIn(
            "state.score",
            source,
        )

        self.assertIn(
            "state.grade",
            source,
        )


if __name__ == "__main__":
    unittest.main()
