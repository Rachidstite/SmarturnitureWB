import unittest
from dataclasses import fields, is_dataclass


class TestSheetUtilizationReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.sheet_utilization_report import (
            SheetUtilizationReport,
        )

        self.assertTrue(is_dataclass(SheetUtilizationReport))

    def test_report_has_required_fields_in_order(self):
        from manufacturing.sheet_utilization_report import (
            SheetUtilizationReport,
        )

        self.assertEqual(
            [field.name for field in fields(SheetUtilizationReport)],
            [
                "total_sheet_area_m2",
                "used_area_m2",
                "waste_area_m2",
                "utilization_percent",
                "waste_percent",
                "warnings",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.sheet_utilization_report import (
            SheetUtilizationReport,
        )

        report = SheetUtilizationReport()

        self.assertEqual(report.total_sheet_area_m2, 0.0)
        self.assertEqual(report.used_area_m2, 0.0)
        self.assertEqual(report.waste_area_m2, 0.0)
        self.assertEqual(report.utilization_percent, 0.0)
        self.assertEqual(report.waste_percent, 0.0)
        self.assertEqual(report.warnings, [])

    def test_warnings_defaults_to_independent_lists(self):
        from manufacturing.sheet_utilization_report import (
            SheetUtilizationReport,
        )

        first_report = SheetUtilizationReport()
        second_report = SheetUtilizationReport()

        self.assertIsNot(first_report.warnings, second_report.warnings)


if __name__ == "__main__":
    unittest.main()
