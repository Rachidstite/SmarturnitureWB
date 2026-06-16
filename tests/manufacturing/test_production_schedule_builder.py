import unittest


class TestProductionScheduleBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.production_schedule_builder import (
            ProductionScheduleBuilder,
        )

        self.assertTrue(callable(ProductionScheduleBuilder().build))

    def test_schedule_is_generated(self):
        from manufacturing.production_schedule_builder import (
            ProductionScheduleBuilder,
        )
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )
        from manufacturing.manufacturing_capacity_report import (
            ManufacturingCapacityReport,
        )

        duration = ManufacturingDurationReport(
            total_production_minutes=960
        )

        capacity = ManufacturingCapacityReport(
            daily_capacity_hours=8.0,
            capacity_utilization_percent=40.0,
        )

        report = ProductionScheduleBuilder().build(
            duration,
            capacity,
        )

        self.assertEqual(report.required_work_days, 2.0)


if __name__ == "__main__":
    unittest.main()
