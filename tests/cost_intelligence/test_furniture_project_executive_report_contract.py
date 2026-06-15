import unittest
from dataclasses import fields, is_dataclass


class TestFurnitureProjectExecutiveReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from cost_intelligence.furniture_project_executive_report import (
            FurnitureProjectExecutiveReport,
        )

        self.assertTrue(is_dataclass(FurnitureProjectExecutiveReport))

    def test_report_has_exact_field_order(self):
        from cost_intelligence.furniture_project_executive_report import (
            FurnitureProjectExecutiveReport,
        )

        self.assertEqual(
            [field.name for field in fields(FurnitureProjectExecutiveReport)],
            [
                "total_cabinets",
                "total_physical_parts",
                "total_machining_operations",
                "overall_score",
                "overall_grade",
                "decision_status",
                "production_status",
                "total_manufacturing_cost",
                "gross_margin_rate",
                "utilization_rate",
                "waste_rate",
                "recovery_score",
                "warnings",
                "recommendations",
            ],
        )

    def test_report_has_safe_defaults(self):
        from cost_intelligence.furniture_project_executive_report import (
            FurnitureProjectExecutiveReport,
        )

        report = FurnitureProjectExecutiveReport()

        self.assertEqual(report.total_cabinets, 0)
        self.assertEqual(report.total_physical_parts, 0)
        self.assertEqual(report.total_machining_operations, 0)
        self.assertEqual(report.overall_score, 0)
        self.assertEqual(report.overall_grade, "F")
        self.assertEqual(report.decision_status, "BLOCKED")
        self.assertEqual(report.production_status, "")
        self.assertEqual(report.total_manufacturing_cost, 0.0)
        self.assertEqual(report.gross_margin_rate, 0.0)
        self.assertEqual(report.utilization_rate, 0.0)
        self.assertEqual(report.waste_rate, 0.0)
        self.assertEqual(report.recovery_score, 0)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.recommendations, [])

    def test_list_defaults_are_independent(self):
        from cost_intelligence.furniture_project_executive_report import (
            FurnitureProjectExecutiveReport,
        )

        first = FurnitureProjectExecutiveReport()
        second = FurnitureProjectExecutiveReport()

        first.warnings.append("warning")
        first.recommendations.append("recommendation")

        self.assertEqual(second.warnings, [])
        self.assertEqual(second.recommendations, [])
        self.assertIsNot(first.warnings, second.warnings)
        self.assertIsNot(first.recommendations, second.recommendations)


if __name__ == "__main__":
    unittest.main()
