import unittest
from dataclasses import fields, is_dataclass


class TestFurnitureProjectBusinessReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from cost_intelligence.furniture_project_business_report import (
            FurnitureProjectBusinessReport,
        )

        self.assertTrue(is_dataclass(FurnitureProjectBusinessReport))

    def test_report_has_exact_field_order(self):
        from cost_intelligence.furniture_project_business_report import (
            FurnitureProjectBusinessReport,
        )

        self.assertEqual(
            [field.name for field in fields(FurnitureProjectBusinessReport)],
            [
                "project_summary",
                "quotation_document",
                "quotation_breakdowns",
                "manufacturing_metrics_report",
                "manufacturing_complexity_report",
                "manufacturing_duration_report",
                "manufacturing_capacity_report",
                "profitability_report",
                "executive_report",
                "factory_decision_report",
            ],
        )

    def test_report_has_safe_defaults(self):
        from cost_intelligence.furniture_project_business_report import (
            FurnitureProjectBusinessReport,
        )

        report = FurnitureProjectBusinessReport()

        self.assertIsNone(report.project_summary)
        self.assertIsNone(report.quotation_document)
        self.assertEqual(report.quotation_breakdowns, [])
        self.assertIsNone(report.manufacturing_metrics_report)
        self.assertIsNone(report.manufacturing_complexity_report)
        self.assertIsNone(report.manufacturing_duration_report)
        self.assertIsNone(report.manufacturing_capacity_report)
        self.assertIsNone(report.profitability_report)
        self.assertIsNone(report.executive_report)
        self.assertIsNone(report.factory_decision_report)

    def test_list_defaults_are_independent(self):
        from cost_intelligence.furniture_project_business_report import (
            FurnitureProjectBusinessReport,
        )

        first = FurnitureProjectBusinessReport()
        second = FurnitureProjectBusinessReport()

        first.quotation_breakdowns.append({"cabinet_index": 1})

        self.assertEqual(second.quotation_breakdowns, [])
        self.assertIsNot(first.quotation_breakdowns, second.quotation_breakdowns)


if __name__ == "__main__":
    unittest.main()
