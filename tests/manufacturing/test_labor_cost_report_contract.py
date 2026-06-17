import unittest
from dataclasses import fields, is_dataclass


class TestLaborCostReportContract(unittest.TestCase):

    def test_report_is_dataclass_with_exact_field_order(self):
        from manufacturing.labor_cost_report import LaborCostReport

        self.assertTrue(is_dataclass(LaborCostReport))
        self.assertEqual(
            [field.name for field in fields(LaborCostReport)],
            [
                "cnc_labor_cost",
                "drilling_labor_cost",
                "edge_banding_labor_cost",
                "assembly_labor_cost",
                "total_labor_cost",
                "currency",
                "warnings",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.labor_cost_report import LaborCostReport

        report = LaborCostReport()

        self.assertEqual(report.cnc_labor_cost, 0.0)
        self.assertEqual(report.drilling_labor_cost, 0.0)
        self.assertEqual(report.edge_banding_labor_cost, 0.0)
        self.assertEqual(report.assembly_labor_cost, 0.0)
        self.assertEqual(report.total_labor_cost, 0.0)
        self.assertEqual(report.currency, "MAD")
        self.assertEqual(report.warnings, [])


if __name__ == "__main__":
    unittest.main()
