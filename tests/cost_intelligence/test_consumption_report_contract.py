import unittest


class TestConsumptionReportContract(unittest.TestCase):

    def test_consumption_report_exists(self):

        try:
            from cost_intelligence.consumption_report import (
                ConsumptionReport,
            )
        except ImportError:
            self.fail(
                "ConsumptionReport does not exist"
            )

    def test_consumption_report_has_required_fields(self):

        from cost_intelligence.consumption_report import (
            ConsumptionReport,
        )

        report = ConsumptionReport()

        self.assertTrue(
            hasattr(report, "material_consumption"),
        )
        self.assertTrue(
            hasattr(report, "sheet_consumption"),
        )
        self.assertTrue(
            hasattr(report, "hardware_consumption"),
        )
        self.assertTrue(
            hasattr(report, "waste_ratio"),
        )
        self.assertTrue(
            hasattr(report, "currency"),
        )
        self.assertTrue(
            hasattr(report, "warnings"),
        )

    def test_consumption_report_can_be_created_from_cost_estimate(self):

        from cost_intelligence.consumption_report import (
            ConsumptionReport,
        )
        from cost_intelligence.cost_estimate import CostEstimate

        estimate = CostEstimate(
            currency="MAD",
            warnings=["Missing hardware quantity"],
        )
        estimate.material_consumption = 0.5
        estimate.sheet_consumption = 1
        estimate.hardware_consumption = 4
        estimate.waste_ratio = 0.30

        report = ConsumptionReport.from_estimate(
            estimate,
        )

        self.assertEqual(
            report.material_consumption,
            0.5,
        )
        self.assertEqual(
            report.sheet_consumption,
            1,
        )
        self.assertEqual(
            report.hardware_consumption,
            4,
        )
        self.assertEqual(
            report.waste_ratio,
            0.30,
        )
        self.assertEqual(
            report.currency,
            "MAD",
        )
        self.assertEqual(
            report.warnings,
            ["Missing hardware quantity"],
        )


if __name__ == "__main__":
    unittest.main()
