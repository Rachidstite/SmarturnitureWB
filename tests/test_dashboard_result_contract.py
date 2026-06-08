import unittest


class TestDashboardResultContract(
    unittest.TestCase
):

    def test_result_has_report_and_viewmodel(self):

        with open(
            "services/manufacturing_dashboard_result.py",
            "r",
            encoding="utf-8",
        ) as f:
            source = f.read()

        self.assertIn(
            "report",
            source,
        )

        self.assertIn(
            "viewmodel",
            source,
        )


if __name__ == "__main__":
    unittest.main()
