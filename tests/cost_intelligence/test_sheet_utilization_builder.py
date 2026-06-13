import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestSheetUtilizationBuilder(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.sheet_utilization_builder import (
            SheetUtilizationBuilder,
        )

        self.builder = SheetUtilizationBuilder()

    def test_report_is_dataclass_with_required_fields(self):
        from cost_intelligence.sheet_utilization_report import (
            SheetUtilizationReport,
        )

        self.assertTrue(is_dataclass(SheetUtilizationReport))
        self.assertEqual(
            [field.name for field in fields(SheetUtilizationReport)],
            [
                "sheet_count",
                "total_sheet_area",
                "total_used_area",
                "total_remaining_area",
                "utilization_rate",
                "waste_rate",
                "warnings",
            ],
        )

    def test_build_aggregates_sheet_utilization(self):
        from exports.strategies import SheetResult

        sheets = [
            SheetResult(
                sheet_id=1,
                sheet_width=100,
                sheet_height=50,
                used_area=2500,
            ),
            SheetResult(
                sheet_id=2,
                sheet_width=200,
                sheet_height=50,
                used_area=5000,
            ),
        ]

        report = self.builder.build(sheets)

        self.assertEqual(report.sheet_count, 2)
        self.assertEqual(report.total_sheet_area, 15000)
        self.assertEqual(report.total_used_area, 7500)
        self.assertEqual(report.total_remaining_area, 7500)
        self.assertEqual(report.utilization_rate, 0.5)
        self.assertEqual(report.waste_rate, 0.5)
        self.assertEqual(report.warnings, [])

    def test_empty_sheet_results_are_safe(self):
        report = self.builder.build([])

        self.assertEqual(report.sheet_count, 0)
        self.assertEqual(report.total_sheet_area, 0)
        self.assertEqual(report.total_used_area, 0)
        self.assertEqual(report.total_remaining_area, 0)
        self.assertEqual(report.utilization_rate, 0.0)
        self.assertEqual(report.waste_rate, 0.0)
        self.assertEqual(report.warnings, ["No sheet results available"])

    def test_missing_or_zero_dimensions_add_warning(self):
        sheets = [
            SimpleNamespace(used_area=0),
            SimpleNamespace(sheet_width=100, sheet_height=0, used_area=0),
        ]

        report = self.builder.build(sheets)

        self.assertEqual(
            report.warnings,
            ["Sheet result has missing or zero dimensions"],
        )

    def test_warnings_list_is_new_for_each_report(self):
        first_report = self.builder.build([])
        second_report = self.builder.build([])

        self.assertIsNot(first_report.warnings, second_report.warnings)


if __name__ == "__main__":
    unittest.main()
