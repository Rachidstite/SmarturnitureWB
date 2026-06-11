import unittest


class TestCostReportContract(unittest.TestCase):

    def test_cost_report_exists(self):

        try:
            from cost_intelligence.cost_report import (
                CostReport,
            )
        except ImportError:
            self.fail(
                "CostReport does not exist"
            )

    def test_cost_report_can_be_created_from_cost_estimate(self):

        from cost_intelligence.cost_estimate import (
            CostEstimate,
        )
        from cost_intelligence.cost_report import (
            CostReport,
        )

        estimate = CostEstimate(
            material_cost=50,
            sheet_cost=560,
            waste_cost=84,
            hardware_cost=48,
            total_cost=608,
            currency="MAD",
        )

        report = CostReport.from_estimate(
            estimate,
        )

        self.assertEqual(
            report.total_cost,
            608,
        )

        self.assertEqual(
            report.currency,
            "MAD",
        )


if __name__ == "__main__":
    unittest.main()
