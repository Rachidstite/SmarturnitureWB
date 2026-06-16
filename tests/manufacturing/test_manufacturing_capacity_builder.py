import unittest


class TestManufacturingCapacityBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.manufacturing_capacity_builder import (
            ManufacturingCapacityBuilder,
        )

        self.assertTrue(callable(ManufacturingCapacityBuilder().build))

    def test_builder_calculates_capacity_from_duration_report(self):
        from manufacturing.manufacturing_capacity_builder import (
            ManufacturingCapacityBuilder,
        )
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = ManufacturingCapacityBuilder().build(
            ManufacturingDurationReport(total_production_minutes=240.0),
            daily_capacity_hours=8.0,
        )

        self.assertEqual(report.total_production_hours, 4.0)
        self.assertEqual(report.daily_capacity_hours, 8.0)
        self.assertEqual(report.estimated_days_required, 0.5)
        self.assertEqual(report.capacity_utilization_percent, 10.0)
        self.assertEqual(report.capacity_status, "AVAILABLE")

    def test_builder_marks_available_under_50_percent(self):
        from manufacturing.manufacturing_capacity_builder import (
            ManufacturingCapacityBuilder,
        )
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = ManufacturingCapacityBuilder().build(
            ManufacturingDurationReport(total_production_minutes=600.0),
            daily_capacity_hours=8.0,
        )

        self.assertEqual(report.capacity_utilization_percent, 25.0)
        self.assertEqual(report.capacity_status, "AVAILABLE")

    def test_builder_marks_limited_between_50_and_85_percent(self):
        from manufacturing.manufacturing_capacity_builder import (
            ManufacturingCapacityBuilder,
        )
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = ManufacturingCapacityBuilder().build(
            ManufacturingDurationReport(total_production_minutes=1800.0),
            daily_capacity_hours=8.0,
        )

        self.assertEqual(report.capacity_utilization_percent, 75.0)
        self.assertEqual(report.capacity_status, "LIMITED")

    def test_builder_marks_overloaded_at_or_above_85_percent(self):
        from manufacturing.manufacturing_capacity_builder import (
            ManufacturingCapacityBuilder,
        )
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = ManufacturingCapacityBuilder().build(
            ManufacturingDurationReport(total_production_minutes=14400.0),
            daily_capacity_hours=8.0,
        )

        self.assertEqual(report.capacity_utilization_percent, 100.0)
        self.assertEqual(report.capacity_status, "OVERLOADED")

    def test_builder_marks_unknown_for_zero_daily_capacity(self):
        from manufacturing.manufacturing_capacity_builder import (
            ManufacturingCapacityBuilder,
        )
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = ManufacturingCapacityBuilder().build(
            ManufacturingDurationReport(total_production_minutes=240.0),
            daily_capacity_hours=0.0,
        )

        self.assertEqual(report.estimated_days_required, 0.0)
        self.assertEqual(report.capacity_utilization_percent, 0.0)
        self.assertEqual(report.capacity_status, "UNKNOWN")
        self.assertEqual(
            report.warnings,
            ["Daily capacity hours must be greater than zero."],
        )

    def test_builder_propagates_warnings_without_mutating_duration_report(self):
        from manufacturing.manufacturing_capacity_builder import (
            ManufacturingCapacityBuilder,
        )
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        duration_report = ManufacturingDurationReport(
            total_production_minutes=240.0,
            warnings=["Duration warning"],
        )

        report = ManufacturingCapacityBuilder().build(duration_report)

        self.assertEqual(report.warnings, ["Duration warning"])
        self.assertEqual(duration_report.warnings, ["Duration warning"])
        self.assertIsNot(report.warnings, duration_report.warnings)


if __name__ == "__main__":
    unittest.main()
