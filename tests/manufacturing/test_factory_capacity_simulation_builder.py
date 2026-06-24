import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestFactoryCapacitySimulationBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.factory_capacity_simulation_builder import (
            FactoryCapacitySimulationBuilder,
        )

        self.builder = FactoryCapacitySimulationBuilder()

    def test_report_contract(self):
        from manufacturing.factory_capacity_simulation_report import (
            FactoryCapacitySimulationReport,
        )

        self.assertTrue(is_dataclass(FactoryCapacitySimulationReport))
        self.assertEqual(
            [field.name for field in fields(FactoryCapacitySimulationReport)],
            [
                "required_factory_minutes",
                "available_factory_minutes",
                "capacity_usage_percent",
                "capacity_status",
                "capacity_recommendation",
            ],
        )

        report = FactoryCapacitySimulationReport()
        self.assertEqual(report.required_factory_minutes, 0.0)
        self.assertEqual(report.available_factory_minutes, 0.0)
        self.assertEqual(report.capacity_usage_percent, 0.0)
        self.assertEqual(report.capacity_status, "AVAILABLE")
        self.assertEqual(report.capacity_recommendation, "")

    def test_required_minutes_copied_from_simulation_report(self):
        report = self.builder.build(
            self._simulation_report(total_minutes=123.4),
            available_factory_minutes=400.0,
        )
        self.assertEqual(report.required_factory_minutes, 123.4)

    def test_capacity_usage_percent_calculated(self):
        report = self.builder.build(
            self._simulation_report(total_minutes=100.0),
            available_factory_minutes=200.0,
        )
        self.assertEqual(report.capacity_usage_percent, 50.0)

    def test_overloaded_at_or_above_100_percent(self):
        report = self.builder.build(
            self._simulation_report(total_minutes=200.0),
            available_factory_minutes=200.0,
        )
        self.assertEqual(report.capacity_status, "OVERLOADED")
        self.assertEqual(report.capacity_recommendation, "Factory capacity exceeded")

    def test_high_load_at_or_above_80_percent(self):
        report = self.builder.build(
            self._simulation_report(total_minutes=160.0),
            available_factory_minutes=200.0,
        )
        self.assertEqual(report.capacity_status, "HIGH_LOAD")
        self.assertEqual(
            report.capacity_recommendation,
            "Factory approaching capacity limit",
        )

    def test_available_below_80_percent(self):
        report = self.builder.build(
            self._simulation_report(total_minutes=79.0),
            available_factory_minutes=100.0,
        )
        self.assertEqual(report.capacity_status, "AVAILABLE")
        self.assertEqual(report.capacity_recommendation, "")

    def test_zero_available_factory_minutes_is_safe(self):
        report = self.builder.build(
            self._simulation_report(total_minutes=10.0),
            available_factory_minutes=0.0,
        )
        self.assertEqual(report.capacity_usage_percent, 0.0)
        self.assertEqual(report.capacity_status, "OVERLOADED")
        self.assertEqual(report.capacity_recommendation, "Factory capacity exceeded")

    def test_builder_does_not_mutate_simulation_report(self):
        simulation_report = self._simulation_report(
            total_minutes=150.0,
            notes=["simulation"],
        )
        snapshot = self._snapshot(simulation_report)

        self.builder.build(simulation_report, available_factory_minutes=200.0)

        self.assertEqual(self._snapshot(simulation_report), snapshot)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _simulation_report(total_minutes=0.0, notes=None):
        report = SimpleNamespace(
            estimated_total_factory_minutes=total_minutes,
            notes=list(notes or []),
        )
        return report


if __name__ == "__main__":
    unittest.main()
