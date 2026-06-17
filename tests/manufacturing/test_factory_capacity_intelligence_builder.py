import unittest


class TestFactoryCapacityIntelligenceBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.factory_capacity_intelligence_builder import (
            FactoryCapacityIntelligenceBuilder,
        )

        self.assertTrue(callable(FactoryCapacityIntelligenceBuilder().build))

    def test_builder_calculates_available_capacity(self):
        from manufacturing.factory_capacity_intelligence_builder import (
            FactoryCapacityIntelligenceBuilder,
        )
        from manufacturing.factory_resource_report import FactoryResourceReport
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = FactoryCapacityIntelligenceBuilder().build(
            FactoryResourceReport(
                workers=3,
                daily_work_hours=8,
                workdays_per_week=5,
                weekly_capacity_hours=120,
            ),
            ManufacturingDurationReport(total_production_minutes=240.0),
        )

        self.assertEqual(report.required_hours, 4.0)
        self.assertEqual(report.weekly_capacity_hours, 120)
        self.assertEqual(report.utilization_percent, (4.0 / 120) * 100)
        self.assertEqual(report.remaining_capacity_hours, 116.0)
        self.assertEqual(report.status, "AVAILABLE")

    def test_builder_calculates_limited_capacity(self):
        from manufacturing.factory_capacity_intelligence_builder import (
            FactoryCapacityIntelligenceBuilder,
        )
        from manufacturing.factory_resource_report import FactoryResourceReport
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = FactoryCapacityIntelligenceBuilder().build(
            FactoryResourceReport(weekly_capacity_hours=20),
            ManufacturingDurationReport(total_production_minutes=1200.0),
        )

        self.assertEqual(report.required_hours, 20.0)
        self.assertEqual(report.utilization_percent, 100.0)
        self.assertEqual(report.remaining_capacity_hours, 0.0)
        self.assertEqual(report.status, "OVERLOADED")

    def test_builder_uses_status_thresholds(self):
        from manufacturing.factory_capacity_intelligence_builder import (
            FactoryCapacityIntelligenceBuilder,
        )
        from manufacturing.factory_resource_report import FactoryResourceReport
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        limited = FactoryCapacityIntelligenceBuilder().build(
            FactoryResourceReport(weekly_capacity_hours=20),
            ManufacturingDurationReport(total_production_minutes=600.0),
        )

        self.assertEqual(limited.utilization_percent, 50.0)
        self.assertEqual(limited.status, "LIMITED")

        overloaded = FactoryCapacityIntelligenceBuilder().build(
            FactoryResourceReport(weekly_capacity_hours=20),
            ManufacturingDurationReport(total_production_minutes=1720.0),
        )

        self.assertEqual(overloaded.utilization_percent, 143.33333333333334)
        self.assertEqual(overloaded.status, "OVERLOADED")

    def test_builder_returns_unknown_for_zero_capacity(self):
        from manufacturing.factory_capacity_intelligence_builder import (
            FactoryCapacityIntelligenceBuilder,
        )
        from manufacturing.factory_resource_report import FactoryResourceReport
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = FactoryCapacityIntelligenceBuilder().build(
            FactoryResourceReport(),
            ManufacturingDurationReport(total_production_minutes=240.0),
        )

        self.assertEqual(report.required_hours, 4.0)
        self.assertEqual(report.weekly_capacity_hours, 0.0)
        self.assertEqual(report.utilization_percent, 0.0)
        self.assertEqual(report.remaining_capacity_hours, 0.0)
        self.assertEqual(report.status, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
