import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingWasteCostReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_waste_cost_report import (
            ManufacturingWasteCostReport,
        )

        self.assertTrue(is_dataclass(ManufacturingWasteCostReport))

    def test_report_has_exact_field_order(self):
        from manufacturing.manufacturing_waste_cost_report import (
            ManufacturingWasteCostReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingWasteCostReport)],
            [
                "waste_area_m2",
                "estimated_waste_cost",
                "sheet_cost",
                "warnings",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.manufacturing_waste_cost_report import (
            ManufacturingWasteCostReport,
        )

        report = ManufacturingWasteCostReport()

        self.assertEqual(report.waste_area_m2, 0.0)
        self.assertEqual(report.estimated_waste_cost, 0.0)
        self.assertEqual(report.sheet_cost, 0.0)
        self.assertEqual(report.warnings, [])

    def test_warning_lists_are_independent(self):
        from manufacturing.manufacturing_waste_cost_report import (
            ManufacturingWasteCostReport,
        )

        first_report = ManufacturingWasteCostReport()
        second_report = ManufacturingWasteCostReport()

        self.assertIsNot(first_report.warnings, second_report.warnings)


if __name__ == "__main__":
    unittest.main()
