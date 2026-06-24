import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestManufacturingExecutiveBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.manufacturing_executive_builder import (
            ManufacturingExecutiveBuilder,
        )

        self.builder = ManufacturingExecutiveBuilder()

    def test_report_contract(self):
        from manufacturing.manufacturing_executive_report import (
            ManufacturingExecutiveReport,
        )

        self.assertTrue(is_dataclass(ManufacturingExecutiveReport))
        self.assertEqual(
            [field.name for field in fields(ManufacturingExecutiveReport)],
            [
                "overall_status",
                "decision_status",
                "manufacturing_status",
                "delivery_status",
                "production_forecast_status",
                "primary_factory_risk",
                "recommended_action",
                "executive_summary",
            ],
        )

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_blocked_decision_is_blocked(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="BLOCKED"),
            self._executive_report(),
            self._delivery_report(),
            self._forecast_report(),
        )
        self.assertEqual(report.overall_status, "BLOCKED")

    def test_delayed_delivery_is_at_risk(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="APPROVED"),
            self._executive_report(),
            self._delivery_report(delivery_status="DELAYED"),
            self._forecast_report(),
        )
        self.assertEqual(report.overall_status, "AT_RISK")

    def test_forecast_delay_risk_is_at_risk(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="APPROVED"),
            self._executive_report(),
            self._delivery_report(delivery_status="ON_TRACK"),
            self._forecast_report(forecast_status="DELAY_RISK"),
        )
        self.assertEqual(report.overall_status, "AT_RISK")

    def test_review_decision_is_review(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="REVIEW_REQUIRED"),
            self._executive_report(),
            self._delivery_report(),
            self._forecast_report(),
        )
        self.assertEqual(report.overall_status, "REVIEW")

    def test_ready_path_is_ready(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="APPROVED"),
            self._executive_report(),
            self._delivery_report(delivery_status="ON_TRACK"),
            self._forecast_report(forecast_status="ON_SCHEDULE"),
        )
        self.assertEqual(report.overall_status, "READY")

    def test_decision_status_is_copied(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="REVIEW_REQUIRED"),
            self._executive_report(),
            self._delivery_report(),
            self._forecast_report(),
        )
        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_manufacturing_status_is_copied(self):
        report = self.builder.build(
            self._model_report(manufacturing_status="REVIEW"),
            self._factory_decision_report(),
            self._executive_report(),
            self._delivery_report(),
            self._forecast_report(),
        )
        self.assertEqual(report.manufacturing_status, "REVIEW")

    def test_delivery_status_is_copied(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(),
            self._executive_report(),
            self._delivery_report(delivery_status="DELAYED"),
            self._forecast_report(),
        )
        self.assertEqual(report.delivery_status, "DELAYED")

    def test_forecast_status_is_copied(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(),
            self._executive_report(),
            self._delivery_report(),
            self._forecast_report(forecast_status="DELAY_RISK"),
        )
        self.assertEqual(report.production_forecast_status, "DELAY_RISK")

    def test_blocked_risk_priority(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="BLOCKED"),
            self._executive_report(main_bottleneck="CNC"),
            self._delivery_report(delivery_status="DELAYED"),
            self._forecast_report(forecast_status="DELAY_RISK"),
        )
        self.assertEqual(report.primary_factory_risk, "BLOCKED")

    def test_delayed_risk_priority(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="APPROVED"),
            self._executive_report(main_bottleneck="CNC"),
            self._delivery_report(delivery_status="DELAYED"),
            self._forecast_report(forecast_status="DELAY_RISK"),
        )
        self.assertEqual(report.primary_factory_risk, "DELAYED")

    def test_forecast_risk_priority(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="APPROVED"),
            self._executive_report(main_bottleneck="CNC"),
            self._delivery_report(delivery_status="ON_TRACK"),
            self._forecast_report(forecast_status="DELAY_RISK"),
        )
        self.assertEqual(report.primary_factory_risk, "DELAY_RISK")

    def test_delivery_risk_priority(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="APPROVED"),
            self._executive_report(delivery_risk="HIGH"),
            self._delivery_report(delivery_status="ON_TRACK"),
            self._forecast_report(forecast_status="ON_SCHEDULE"),
        )
        self.assertEqual(report.primary_factory_risk, "HIGH_DELIVERY_RISK")

    def test_bottleneck_priority(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="APPROVED"),
            self._executive_report(main_bottleneck="CNC"),
            self._delivery_report(delivery_status="ON_TRACK"),
            self._forecast_report(forecast_status="ON_SCHEDULE"),
        )
        self.assertEqual(report.primary_factory_risk, "BOTTLENECK")

    def test_recommendation_from_decision_report(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(recommendations=["Fix one", "Fix two"]),
            self._executive_report(priority_action="Executive action"),
            self._delivery_report(delivery_recommendation="Delivery action"),
            self._forecast_report(forecast_recommendation="Forecast action"),
        )
        self.assertEqual(report.recommended_action, "Fix one; Fix two")

    def test_recommendation_fallback_to_executive_report(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(),
            self._executive_report(priority_action="Executive action"),
            self._delivery_report(delivery_recommendation="Delivery action"),
            self._forecast_report(forecast_recommendation="Forecast action"),
        )
        self.assertEqual(report.recommended_action, "Executive action")

    def test_recommendation_fallback_to_delivery_report(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(),
            self._executive_report(),
            self._delivery_report(delivery_recommendation="Delivery action"),
            self._forecast_report(forecast_recommendation="Forecast action"),
        )
        self.assertEqual(report.recommended_action, "Delivery action")

    def test_recommendation_fallback_to_forecast_report(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(),
            self._executive_report(),
            self._delivery_report(),
            self._forecast_report(forecast_recommendation="Forecast action"),
        )
        self.assertEqual(report.recommended_action, "Forecast action")

    def test_ready_summary(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="APPROVED"),
            self._executive_report(),
            self._delivery_report(delivery_status="ON_TRACK"),
            self._forecast_report(forecast_status="ON_SCHEDULE"),
        )
        self.assertEqual(report.executive_summary, "Factory ready for production.")

    def test_review_summary(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="REVIEW_REQUIRED"),
            self._executive_report(),
            self._delivery_report(delivery_status="ON_TRACK"),
            self._forecast_report(forecast_status="ON_SCHEDULE"),
        )
        self.assertEqual(
            report.executive_summary,
            "Factory review required before production.",
        )

    def test_at_risk_summary(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="APPROVED"),
            self._executive_report(),
            self._delivery_report(delivery_status="DELAYED"),
            self._forecast_report(forecast_status="ON_SCHEDULE"),
        )
        self.assertEqual(report.executive_summary, "Production or delivery risk detected.")

    def test_blocked_summary(self):
        report = self.builder.build(
            self._model_report(),
            self._factory_decision_report(decision_status="BLOCKED"),
            self._executive_report(),
            self._delivery_report(delivery_status="ON_TRACK"),
            self._forecast_report(forecast_status="ON_SCHEDULE"),
        )
        self.assertEqual(report.executive_summary, "Manufacturing is blocked.")

    def test_no_input_mutation(self):
        model = self._model_report(
            manufacturing_status="READY",
            warnings=["model"],
            recommendations=["model rec"],
            metadata={"a": 1},
        )
        decision = self._factory_decision_report(
            decision_status="APPROVED",
            recommendations=["decision"],
            warnings=["decision warning"],
            blocking_issues=["decision issue"],
            metadata={"b": 2},
        )
        executive = self._executive_report(
            factory_status="STABLE",
            main_bottleneck="CNC",
            priority_action="executive",
            metadata={"c": 3},
        )
        delivery = self._delivery_report(
            delivery_status="ON_TRACK",
            delivery_recommendation="delivery",
            metadata={"d": 4},
        )
        forecast = self._forecast_report(
            forecast_status="ON_SCHEDULE",
            forecast_recommendation="forecast",
            metadata={"e": 5},
        )
        snapshots = [self._snapshot(obj) for obj in (model, decision, executive, delivery, forecast)]

        self.builder.build(model, decision, executive, delivery, forecast)

        self.assertEqual(
            [self._snapshot(obj) for obj in (model, decision, executive, delivery, forecast)],
            snapshots,
        )

    @staticmethod
    def _snapshot(obj):
        return {
            key: list(value) if isinstance(value, list) else dict(value) if isinstance(value, dict) else value
            for key, value in obj.__dict__.items()
        }

    @staticmethod
    def _model_report(manufacturing_status="UNKNOWN", warnings=None, recommendations=None, metadata=None):
        from manufacturing.manufacturing_model_report import ManufacturingModelReport

        report = ManufacturingModelReport(manufacturing_status=manufacturing_status)
        report.warnings = list(warnings or [])
        report.recommendations = list(recommendations or [])
        report.metadata = dict(metadata or {})
        return report

    @staticmethod
    def _factory_decision_report(
        decision_status="APPROVED",
        recommendations=None,
        warnings=None,
        blocking_issues=None,
        metadata=None,
        factory_bottleneck="",
    ):
        from cost_intelligence.factory_decision_report import FactoryDecisionReport

        report = FactoryDecisionReport(decision_status=decision_status)
        report.recommendations = list(recommendations or [])
        report.warnings = list(warnings or [])
        report.blocking_issues = list(blocking_issues or [])
        report.metadata = dict(metadata or {})
        report.factory_bottleneck = factory_bottleneck
        return report

    @staticmethod
    def _executive_report(
        factory_status="STABLE",
        main_bottleneck="",
        delivery_risk="LOW",
        priority_action="",
        metadata=None,
    ):
        from manufacturing.factory_executive_intelligence_report import (
            FactoryExecutiveIntelligenceReport,
        )

        report = FactoryExecutiveIntelligenceReport(
            factory_status=factory_status,
            main_bottleneck=main_bottleneck,
            delivery_risk=delivery_risk,
            priority_action=priority_action,
        )
        report.metadata = dict(metadata or {})
        return report

    @staticmethod
    def _delivery_report(
        delivery_status="ON_TRACK",
        delivery_recommendation="",
        metadata=None,
    ):
        from manufacturing.factory_delivery_report import FactoryDeliveryReport

        report = FactoryDeliveryReport(
            delivery_status=delivery_status,
            delivery_recommendation=delivery_recommendation,
        )
        report.metadata = dict(metadata or {})
        return report

    @staticmethod
    def _forecast_report(
        forecast_status="ON_SCHEDULE",
        forecast_recommendation="",
        metadata=None,
    ):
        from manufacturing.production_forecast_report import ProductionForecastReport

        report = ProductionForecastReport(
            forecast_status=forecast_status,
            forecast_recommendation=forecast_recommendation,
        )
        report.metadata = dict(metadata or {})
        return report


if __name__ == "__main__":
    unittest.main()
