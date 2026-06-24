import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestFactoryOperationalBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.factory_operational_builder import (
            FactoryOperationalBuilder,
        )

        self.builder = FactoryOperationalBuilder()

    def test_report_contract(self):
        from manufacturing.factory_operational_report import FactoryOperationalReport

        self.assertTrue(is_dataclass(FactoryOperationalReport))
        self.assertEqual(
            [field.name for field in fields(FactoryOperationalReport)],
            [
                "operational_status",
                "delivery_risk",
                "capacity_risk",
                "management_recommendation",
            ],
        )

        report = FactoryOperationalReport()

        self.assertEqual(report.operational_status, "READY")
        self.assertEqual(report.delivery_risk, "LOW")
        self.assertEqual(report.capacity_risk, "LOW")
        self.assertEqual(report.management_recommendation, "")

    def test_blocked_readiness_blocks_operational_status(self):
        report = self.builder.build(
            self._readiness_report(readiness_status="BLOCKED"),
            self._schedule_report(),
            self._bottleneck_report(),
        )

        self.assertEqual(report.operational_status, "BLOCKED")
        self.assertEqual(
            report.management_recommendation,
            "Project should not enter production",
        )

    def test_high_schedule_risk_sets_delivery_risk_high(self):
        report = self.builder.build(
            self._readiness_report(),
            self._schedule_report(schedule_risk_level="HIGH"),
            self._bottleneck_report(),
        )

        self.assertEqual(report.delivery_risk, "HIGH")
        self.assertEqual(report.management_recommendation, "Schedule review required")

    def test_high_bottleneck_severity_sets_capacity_risk_high(self):
        report = self.builder.build(
            self._readiness_report(),
            self._schedule_report(),
            self._bottleneck_report(severity="HIGH"),
        )

        self.assertEqual(report.capacity_risk, "HIGH")
        self.assertEqual(report.management_recommendation, "Factory capacity review required")

    def test_ready_defaults(self):
        report = self.builder.build(
            self._readiness_report(),
            self._schedule_report(),
            self._bottleneck_report(),
        )

        self.assertEqual(report.operational_status, "READY")
        self.assertEqual(report.delivery_risk, "LOW")
        self.assertEqual(report.capacity_risk, "LOW")
        self.assertEqual(report.management_recommendation, "")

    def test_builder_does_not_mutate_inputs(self):
        readiness = self._readiness_report(readiness_status="BLOCKED", tags=["a"])
        schedule = self._schedule_report(schedule_risk_level="HIGH", tags=["b"])
        bottleneck = self._bottleneck_report(severity="HIGH", tags=["c"])
        snapshots = [
            self._snapshot(readiness),
            self._snapshot(schedule),
            self._snapshot(bottleneck),
        ]

        self.builder.build(readiness, schedule, bottleneck)

        self.assertEqual(
            [self._snapshot(readiness), self._snapshot(schedule), self._snapshot(bottleneck)],
            snapshots,
        )

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _readiness_report(readiness_status="READY", tags=None):
        return SimpleNamespace(
            readiness_status=readiness_status,
            tags=list(tags or []),
        )

    @staticmethod
    def _schedule_report(schedule_risk_level="LOW", tags=None):
        from manufacturing.production_schedule_report import ProductionScheduleReport

        report = ProductionScheduleReport(schedule_risk_level=schedule_risk_level)
        report.tags = list(tags or [])
        return report

    @staticmethod
    def _bottleneck_report(severity="LOW", tags=None):
        from manufacturing.factory_bottleneck_intelligence_report import (
            FactoryBottleneckIntelligenceReport,
        )

        report = FactoryBottleneckIntelligenceReport(severity=severity)
        report.tags = list(tags or [])
        return report


if __name__ == "__main__":
    unittest.main()
