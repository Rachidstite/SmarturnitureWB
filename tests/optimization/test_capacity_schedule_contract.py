import importlib
import inspect
import unittest
from types import SimpleNamespace


class TestCapacityScheduleContract(unittest.TestCase):
    def test_manufacturing_duration_influences_capacity(self):
        from manufacturing.manufacturing_capacity_builder import (
            ManufacturingCapacityBuilder,
        )

        report = ManufacturingCapacityBuilder().build(
            SimpleNamespace(
                total_production_minutes=8 * 60 * 4,
                warnings=["capacity-warning"],
            ),
            daily_capacity_hours=8.0,
        )

        self.assertGreater(report.capacity_utilization_percent, 0.0)
        self.assertIn(report.capacity_status, {"AVAILABLE", "LIMITED", "OVERLOADED"})
        self.assertIn("capacity-warning", report.warnings)

    def test_capacity_estimation_influences_scheduling(self):
        from manufacturing.production_schedule_builder import ProductionScheduleBuilder

        report = ProductionScheduleBuilder().build(
            SimpleNamespace(total_production_minutes=8 * 60 * 5, warnings=["duration"]),
            SimpleNamespace(
                daily_capacity_hours=8.0,
                capacity_utilization_percent=90.0,
                warnings=["capacity"],
            ),
        )

        self.assertEqual(report.schedule_risk_level, "HIGH")
        self.assertIn("duration", report.warnings)
        self.assertIn("capacity", report.warnings)

    def test_scheduling_must_influence_factory_bottleneck_intelligence(self):
        source = inspect.getsource(
            importlib.import_module("manufacturing.factory_bottleneck_intelligence_builder")
        )

        self.assertRegex(
            source,
            r"schedule|workload",
        )

    def test_factory_bottleneck_intelligence_influences_factory_decisions(self):
        source = inspect.getsource(
            importlib.import_module("cost_intelligence.factory_decision_intelligence_builder")
        )

        self.assertIn("factory_bottleneck_intelligence_report", source)
        self.assertIn("severity", source)
        self.assertIn("impact", source)


if __name__ == "__main__":
    unittest.main()
