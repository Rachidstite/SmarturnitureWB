import unittest
from dataclasses import fields, is_dataclass


class TestFactoryDecisionReportContract(unittest.TestCase):

    def test_report_is_dataclass_with_exact_field_order(self):
        from cost_intelligence.factory_decision_report import FactoryDecisionReport

        self.assertTrue(is_dataclass(FactoryDecisionReport))
        self.assertEqual(
            [field.name for field in fields(FactoryDecisionReport)],
            [
                "decision_status",
                "manufacturing_ready",
                "profitability_ok",
                "cost_risk_level",
                "waste_risk_level",
                "nesting_risk_level",
                "quotation_risk_level",
                "margin_status",
                "capacity_status",
                "schedule_risk_level",
                "workload_status",
                "complexity_level",
                "blocking_issues",
                "warnings",
                "recommendations",
            ],
        )

    def test_report_has_safe_defaults(self):
        from cost_intelligence.factory_decision_report import FactoryDecisionReport

        report = FactoryDecisionReport()

        self.assertEqual(report.decision_status, "BLOCKED")
        self.assertFalse(report.manufacturing_ready)
        self.assertFalse(report.profitability_ok)
        self.assertEqual(report.cost_risk_level, "LOW")
        self.assertEqual(report.waste_risk_level, "LOW")
        self.assertEqual(report.nesting_risk_level, "LOW")
        self.assertEqual(report.quotation_risk_level, "UNKNOWN")
        self.assertEqual(report.margin_status, "UNKNOWN")
        self.assertEqual(report.capacity_status, "AVAILABLE")
        self.assertEqual(report.schedule_risk_level, "LOW")
        self.assertEqual(report.workload_status, "AVAILABLE")
        self.assertEqual(report.complexity_level, "LOW")
        self.assertEqual(report.blocking_issues, [])
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.recommendations, [])

    def test_report_list_defaults_are_independent(self):
        from cost_intelligence.factory_decision_report import FactoryDecisionReport

        first = FactoryDecisionReport()
        second = FactoryDecisionReport()

        self.assertIsNot(first.blocking_issues, second.blocking_issues)
        self.assertIsNot(first.warnings, second.warnings)
        self.assertIsNot(first.recommendations, second.recommendations)


if __name__ == "__main__":
    unittest.main()
