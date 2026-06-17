import unittest
from dataclasses import fields, is_dataclass


class TestFactoryCapacityIntelligenceReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.factory_capacity_intelligence_report import (
            FactoryCapacityIntelligenceReport,
        )

        self.assertTrue(is_dataclass(FactoryCapacityIntelligenceReport))

    def test_report_has_required_fields_in_order(self):
        from manufacturing.factory_capacity_intelligence_report import (
            FactoryCapacityIntelligenceReport,
        )

        self.assertEqual(
            [field.name for field in fields(FactoryCapacityIntelligenceReport)],
            [
                "required_hours",
                "weekly_capacity_hours",
                "utilization_percent",
                "remaining_capacity_hours",
                "status",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.factory_capacity_intelligence_report import (
            FactoryCapacityIntelligenceReport,
        )

        report = FactoryCapacityIntelligenceReport()

        self.assertEqual(report.required_hours, 0.0)
        self.assertEqual(report.weekly_capacity_hours, 0.0)
        self.assertEqual(report.utilization_percent, 0.0)
        self.assertEqual(report.remaining_capacity_hours, 0.0)
        self.assertEqual(report.status, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
