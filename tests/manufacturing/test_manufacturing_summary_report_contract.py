import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingSummaryReportContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        self.assertTrue(is_dataclass(ManufacturingSummaryReport))

    def test_contract_has_required_fields(self):
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingSummaryReport)],
            [
                "total_panels",
                "total_materials",
                "total_edge_operations",
                "total_machining_operations",
                "warnings",
            ],
        )

    def test_contract_defaults(self):
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        report = ManufacturingSummaryReport()

        self.assertEqual(report.total_panels, 0)
        self.assertEqual(report.total_materials, 0)
        self.assertEqual(report.total_edge_operations, 0)
        self.assertEqual(report.total_machining_operations, 0)
        self.assertEqual(report.warnings, [])

    def test_warning_defaults_are_independent(self):
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        first_report = ManufacturingSummaryReport()
        second_report = ManufacturingSummaryReport()

        self.assertIsNot(first_report.warnings, second_report.warnings)


if __name__ == "__main__":
    unittest.main()
