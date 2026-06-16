import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingCapacityReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_capacity_report import (
            ManufacturingCapacityReport,
        )

        self.assertTrue(is_dataclass(ManufacturingCapacityReport))

    def test_report_has_required_fields_in_order(self):
        from manufacturing.manufacturing_capacity_report import (
            ManufacturingCapacityReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingCapacityReport)],
            [
                "total_production_hours",
                "daily_capacity_hours",
                "estimated_days_required",
                "capacity_utilization_percent",
                "capacity_status",
                "warnings",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.manufacturing_capacity_report import (
            ManufacturingCapacityReport,
        )

        report = ManufacturingCapacityReport()

        self.assertEqual(report.total_production_hours, 0.0)
        self.assertEqual(report.daily_capacity_hours, 8.0)
        self.assertEqual(report.estimated_days_required, 0.0)
        self.assertEqual(report.capacity_utilization_percent, 0.0)
        self.assertEqual(report.capacity_status, "AVAILABLE")
        self.assertEqual(report.warnings, [])

    def test_warnings_defaults_to_independent_lists(self):
        from manufacturing.manufacturing_capacity_report import (
            ManufacturingCapacityReport,
        )

        first_report = ManufacturingCapacityReport()
        second_report = ManufacturingCapacityReport()

        self.assertIsNot(first_report.warnings, second_report.warnings)


if __name__ == "__main__":
    unittest.main()
