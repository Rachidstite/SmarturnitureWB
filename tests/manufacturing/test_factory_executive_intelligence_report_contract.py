import unittest
from dataclasses import fields, is_dataclass


class TestFactoryExecutiveIntelligenceReportContract(unittest.TestCase):

    def test_report_is_dataclass_with_exact_field_order(self):
        from manufacturing.factory_executive_intelligence_report import (
            FactoryExecutiveIntelligenceReport,
        )

        self.assertTrue(is_dataclass(FactoryExecutiveIntelligenceReport))
        self.assertEqual(
            [field.name for field in fields(FactoryExecutiveIntelligenceReport)],
            [
                "factory_status",
                "capacity_status",
                "load_status",
                "main_bottleneck",
                "delivery_confidence",
                "delivery_risk",
                "priority_action",
                "summary",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.factory_executive_intelligence_report import (
            FactoryExecutiveIntelligenceReport,
        )

        report = FactoryExecutiveIntelligenceReport()

        self.assertEqual(report.factory_status, "STABLE")
        self.assertEqual(report.capacity_status, "UNKNOWN")
        self.assertEqual(report.load_status, "LOW")
        self.assertEqual(report.main_bottleneck, "")
        self.assertEqual(report.delivery_confidence, "LOW")
        self.assertEqual(report.delivery_risk, "HIGH")
        self.assertEqual(report.priority_action, "")
        self.assertEqual(report.summary, "Factory intelligence available.")


if __name__ == "__main__":
    unittest.main()
