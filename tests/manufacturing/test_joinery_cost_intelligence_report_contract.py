import unittest
from dataclasses import fields, is_dataclass


class TestJoineryCostIntelligenceReportContract(unittest.TestCase):

    def test_report_is_dataclass_with_exact_field_order(self):
        from manufacturing.joinery_cost_intelligence_report import (
            JoineryCostIntelligenceReport,
        )

        self.assertTrue(is_dataclass(JoineryCostIntelligenceReport))
        self.assertEqual(
            [field.name for field in fields(JoineryCostIntelligenceReport)],
            [
                "total_joinery_cost",
                "minifix_cost",
                "hinge_cost",
                "drawer_slide_cost",
                "handle_cost",
                "cost_breakdown",
                "warnings",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.joinery_cost_intelligence_report import (
            JoineryCostIntelligenceReport,
        )

        report = JoineryCostIntelligenceReport()

        self.assertEqual(report.total_joinery_cost, 0.0)
        self.assertEqual(report.minifix_cost, 0.0)
        self.assertEqual(report.hinge_cost, 0.0)
        self.assertEqual(report.drawer_slide_cost, 0.0)
        self.assertEqual(report.handle_cost, 0.0)
        self.assertEqual(report.cost_breakdown, {})
        self.assertEqual(report.warnings, [])


if __name__ == "__main__":
    unittest.main()
