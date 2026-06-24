import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestFactoryKPIDashboardBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.factory_kpi_dashboard_builder import (
            FactoryKPIDashboardBuilder,
        )

        self.builder = FactoryKPIDashboardBuilder()

    def test_report_contract(self):
        from manufacturing.factory_kpi_dashboard_report import (
            FactoryKPIDashboardReport,
        )

        self.assertTrue(is_dataclass(FactoryKPIDashboardReport))
        self.assertEqual(
            [field.name for field in fields(FactoryKPIDashboardReport)],
            [
                "factory_status",
                "capacity_usage_percent",
                "forecast_days",
                "delivery_status",
                "main_bottleneck",
                "total_manufacturing_cost",
                "hardware_cost",
                "waste_cost",
                "recovered_value",
                "dashboard_recommendation",
            ],
        )

    def test_safe_defaults(self):
        report = self.builder.build()
        self.assertEqual(report.factory_status, "UNKNOWN")
        self.assertEqual(report.capacity_usage_percent, 0.0)
        self.assertEqual(report.forecast_days, 0.0)
        self.assertEqual(report.delivery_status, "UNKNOWN")
        self.assertEqual(report.main_bottleneck, "")
        self.assertEqual(report.total_manufacturing_cost, 0.0)
        self.assertEqual(report.hardware_cost, 0.0)
        self.assertEqual(report.waste_cost, 0.0)
        self.assertEqual(report.recovered_value, 0.0)
        self.assertEqual(report.dashboard_recommendation, "")

    def test_maps_factory_status(self):
        report = self.builder.build(
            factory_executive_intelligence_report=self._executive_report(
                factory_status="CRITICAL"
            )
        )
        self.assertEqual(report.factory_status, "CRITICAL")

    def test_maps_capacity_usage_percent(self):
        report = self.builder.build(
            factory_capacity_simulation_report=self._capacity_report(
                capacity_usage_percent=87.5
            )
        )
        self.assertEqual(report.capacity_usage_percent, 87.5)

    def test_maps_forecast_days(self):
        report = self.builder.build(
            production_forecast_report=self._forecast_report(
                estimated_production_days=7.25
            )
        )
        self.assertEqual(report.forecast_days, 7.25)

    def test_maps_delivery_status(self):
        report = self.builder.build(
            factory_delivery_report=self._delivery_report(delivery_status="DELAYED")
        )
        self.assertEqual(report.delivery_status, "DELAYED")

    def test_maps_main_bottleneck(self):
        report = self.builder.build(
            factory_executive_intelligence_report=self._executive_report(
                main_bottleneck="CNC"
            )
        )
        self.assertEqual(report.main_bottleneck, "CNC")

    def test_maps_manufacturing_cost_fields(self):
        report = self.builder.build(
            factory_decision_report=self._decision_report(
                total_manufacturing_cost=1250.0,
                hardware_cost=250.0,
                waste_cost=50.0,
                recovered_value=40.0,
            )
        )
        self.assertEqual(report.total_manufacturing_cost, 1250.0)
        self.assertEqual(report.hardware_cost, 250.0)
        self.assertEqual(report.waste_cost, 50.0)
        self.assertEqual(report.recovered_value, 40.0)

    def test_critical_factory_status_creates_management_recommendation(self):
        report = self.builder.build(
            factory_executive_intelligence_report=self._executive_report(
                factory_status="CRITICAL"
            )
        )
        self.assertEqual(
            report.dashboard_recommendation,
            "Factory requires immediate management attention",
        )

    def test_delayed_delivery_creates_delivery_recommendation(self):
        report = self.builder.build(
            factory_delivery_report=self._delivery_report(delivery_status="DELAYED")
        )
        self.assertEqual(report.dashboard_recommendation, "Delivery should be reviewed")

    def test_high_capacity_usage_creates_capacity_recommendation(self):
        report = self.builder.build(
            factory_capacity_simulation_report=self._capacity_report(
                capacity_usage_percent=80.0
            )
        )
        self.assertEqual(report.dashboard_recommendation, "Capacity should be monitored")

    def test_builder_does_not_mutate_inputs(self):
        executive = self._executive_report(
            factory_status="CRITICAL",
            main_bottleneck="CNC",
            tags=["exec"],
        )
        capacity = self._capacity_report(
            capacity_usage_percent=90.0,
            tags=["capacity"],
        )
        forecast = self._forecast_report(
            estimated_production_days=12.0,
            tags=["forecast"],
        )
        delivery = self._delivery_report(
            delivery_status="AT_RISK",
            tags=["delivery"],
        )
        decision = self._decision_report(
            total_manufacturing_cost=1000.0,
            hardware_cost=200.0,
            waste_cost=30.0,
            recovered_value=20.0,
            tags=["decision"],
        )
        inputs = [executive, capacity, forecast, delivery, decision]
        snapshots = [self._snapshot(report) for report in inputs]

        self.builder.build(*inputs)

        self.assertEqual([self._snapshot(report) for report in inputs], snapshots)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _executive_report(factory_status="UNKNOWN", main_bottleneck="", tags=None):
        return SimpleNamespace(
            factory_status=factory_status,
            main_bottleneck=main_bottleneck,
            tags=list(tags or []),
        )

    @staticmethod
    def _capacity_report(capacity_usage_percent=0.0, tags=None):
        return SimpleNamespace(
            capacity_usage_percent=capacity_usage_percent,
            tags=list(tags or []),
        )

    @staticmethod
    def _forecast_report(estimated_production_days=0.0, tags=None):
        return SimpleNamespace(
            estimated_production_days=estimated_production_days,
            tags=list(tags or []),
        )

    @staticmethod
    def _delivery_report(delivery_status="UNKNOWN", tags=None):
        return SimpleNamespace(
            delivery_status=delivery_status,
            tags=list(tags or []),
        )

    @staticmethod
    def _decision_report(
        total_manufacturing_cost=0.0,
        hardware_cost=0.0,
        waste_cost=0.0,
        recovered_value=0.0,
        tags=None,
    ):
        return SimpleNamespace(
            total_manufacturing_cost=total_manufacturing_cost,
            hardware_cost=hardware_cost,
            waste_cost=waste_cost,
            recovered_value=recovered_value,
            tags=list(tags or []),
        )


if __name__ == "__main__":
    unittest.main()
