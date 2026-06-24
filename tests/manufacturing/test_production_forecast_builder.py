import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestProductionForecastBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.production_forecast_builder import (
            ProductionForecastBuilder,
        )

        self.builder = ProductionForecastBuilder()

    def test_report_contract(self):
        from manufacturing.production_forecast_report import (
            ProductionForecastReport,
        )

        self.assertTrue(is_dataclass(ProductionForecastReport))
        self.assertEqual(
            [field.name for field in fields(ProductionForecastReport)],
            [
                "required_factory_minutes",
                "available_factory_minutes_per_day",
                "estimated_production_days",
                "forecast_status",
                "forecast_recommendation",
            ],
        )

        report = ProductionForecastReport()
        self.assertEqual(report.required_factory_minutes, 0.0)
        self.assertEqual(report.available_factory_minutes_per_day, 0.0)
        self.assertEqual(report.estimated_production_days, 0.0)
        self.assertEqual(report.forecast_status, "ON_SCHEDULE")
        self.assertEqual(report.forecast_recommendation, "")

    def test_estimated_days_calculated(self):
        report = self.builder.build(
            self._simulation_report(total_minutes=600.0),
            available_factory_minutes_per_day=120.0,
        )
        self.assertEqual(report.estimated_production_days, 5.0)

    def test_delay_risk_above_ten_days(self):
        report = self.builder.build(
            self._simulation_report(total_minutes=1320.0),
            available_factory_minutes_per_day=120.0,
        )
        self.assertEqual(report.forecast_status, "DELAY_RISK")
        self.assertEqual(
            report.forecast_recommendation,
            "Production completion risk detected",
        )

    def test_review_above_five_days(self):
        report = self.builder.build(
            self._simulation_report(total_minutes=720.0),
            available_factory_minutes_per_day=100.0,
        )
        self.assertEqual(report.forecast_status, "REVIEW")
        self.assertEqual(report.forecast_recommendation, "Review production planning")

    def test_on_schedule_at_or_below_five_days(self):
        report = self.builder.build(
            self._simulation_report(total_minutes=500.0),
            available_factory_minutes_per_day=100.0,
        )
        self.assertEqual(report.forecast_status, "ON_SCHEDULE")
        self.assertEqual(report.forecast_recommendation, "")

    def test_safe_defaults_for_zero_capacity(self):
        report = self.builder.build(
            self._simulation_report(total_minutes=500.0),
            available_factory_minutes_per_day=0.0,
        )
        self.assertEqual(report.estimated_production_days, 0.0)
        self.assertEqual(report.forecast_status, "ON_SCHEDULE")
        self.assertEqual(report.forecast_recommendation, "")

    def test_builder_does_not_mutate_simulation_report(self):
        simulation_report = self._simulation_report(
            total_minutes=300.0,
            notes=["forecast"],
        )
        snapshot = self._snapshot(simulation_report)

        self.builder.build(simulation_report, available_factory_minutes_per_day=60.0)

        self.assertEqual(self._snapshot(simulation_report), snapshot)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _simulation_report(total_minutes=0.0, notes=None):
        return SimpleNamespace(
            estimated_total_factory_minutes=total_minutes,
            notes=list(notes or []),
        )


if __name__ == "__main__":
    unittest.main()
