import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestFactoryDeliveryBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.factory_delivery_builder import FactoryDeliveryBuilder

        self.builder = FactoryDeliveryBuilder()

    def test_report_contract(self):
        from manufacturing.factory_delivery_report import FactoryDeliveryReport

        self.assertTrue(is_dataclass(FactoryDeliveryReport))
        self.assertEqual(
            [field.name for field in fields(FactoryDeliveryReport)],
            [
                "delivery_status",
                "delivery_confidence",
                "delivery_recommendation",
            ],
        )

        report = FactoryDeliveryReport()

        self.assertEqual(report.delivery_status, "ON_TRACK")
        self.assertEqual(report.delivery_confidence, "HIGH")
        self.assertEqual(report.delivery_recommendation, "")

    def test_blocked_operational_status_delays_delivery(self):
        report = self.builder.build(
            self._operational_report(operational_status="BLOCKED"),
            self._schedule_report(),
        )

        self.assertEqual(report.delivery_status, "DELAYED")
        self.assertEqual(report.delivery_confidence, "LOW")
        self.assertEqual(report.delivery_recommendation, "Delivery is delayed")

    def test_high_delivery_risk_sets_at_risk(self):
        report = self.builder.build(
            self._operational_report(delivery_risk="HIGH"),
            self._schedule_report(),
        )

        self.assertEqual(report.delivery_status, "AT_RISK")
        self.assertEqual(report.delivery_confidence, "MEDIUM")
        self.assertEqual(report.delivery_recommendation, "Delivery review required")

    def test_high_schedule_risk_sets_at_risk(self):
        report = self.builder.build(
            self._operational_report(),
            self._schedule_report(schedule_risk_level="HIGH"),
        )

        self.assertEqual(report.delivery_status, "AT_RISK")

    def test_on_track_produces_high_confidence(self):
        report = self.builder.build(
            self._operational_report(),
            self._schedule_report(),
        )

        self.assertEqual(report.delivery_status, "ON_TRACK")
        self.assertEqual(report.delivery_confidence, "HIGH")
        self.assertEqual(report.delivery_recommendation, "")

    def test_builder_does_not_mutate_inputs(self):
        operational = self._operational_report(
            operational_status="BLOCKED",
            delivery_risk="HIGH",
            tags=["a"],
        )
        schedule = self._schedule_report(
            schedule_risk_level="HIGH",
            tags=["b"],
        )
        snapshots = [self._snapshot(operational), self._snapshot(schedule)]

        self.builder.build(operational, schedule)

        self.assertEqual([self._snapshot(operational), self._snapshot(schedule)], snapshots)

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _operational_report(operational_status="READY", delivery_risk="LOW", tags=None):
        from manufacturing.factory_operational_report import FactoryOperationalReport

        report = FactoryOperationalReport(
            operational_status=operational_status,
            delivery_risk=delivery_risk,
        )
        report.tags = list(tags or [])
        return report

    @staticmethod
    def _schedule_report(schedule_risk_level="LOW", tags=None):
        from manufacturing.production_schedule_report import ProductionScheduleReport

        report = ProductionScheduleReport(schedule_risk_level=schedule_risk_level)
        report.tags = list(tags or [])
        return report


if __name__ == "__main__":
    unittest.main()
