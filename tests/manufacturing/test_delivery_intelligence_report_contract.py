import unittest
from dataclasses import fields, is_dataclass


class TestDeliveryIntelligenceReportContract(unittest.TestCase):

    def test_report_is_dataclass_with_exact_field_order(self):
        from manufacturing.delivery_intelligence_report import (
            DeliveryIntelligenceReport,
        )

        self.assertTrue(is_dataclass(DeliveryIntelligenceReport))
        self.assertEqual(
            [field.name for field in fields(DeliveryIntelligenceReport)],
            [
                "estimated_hours",
                "estimated_days",
                "confidence",
                "delivery_risk",
                "recommendation",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.delivery_intelligence_report import (
            DeliveryIntelligenceReport,
        )

        report = DeliveryIntelligenceReport()

        self.assertEqual(report.estimated_hours, 0.0)
        self.assertEqual(report.estimated_days, 0.0)
        self.assertEqual(report.confidence, "LOW")
        self.assertEqual(report.delivery_risk, "HIGH")
        self.assertEqual(report.recommendation, "Review delivery plan")


if __name__ == "__main__":
    unittest.main()
