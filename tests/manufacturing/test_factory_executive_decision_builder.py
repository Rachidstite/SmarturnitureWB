import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestFactoryExecutiveDecisionBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.factory_executive_decision_builder import (
            FactoryExecutiveDecisionBuilder,
        )

        self.builder = FactoryExecutiveDecisionBuilder()

    def test_report_contract(self):
        from manufacturing.factory_executive_decision_report import (
            FactoryExecutiveDecisionReport,
        )

        self.assertTrue(is_dataclass(FactoryExecutiveDecisionReport))
        self.assertEqual(
            [field.name for field in fields(FactoryExecutiveDecisionReport)],
            [
                "business_status",
                "profitability_status",
                "delivery_status",
                "executive_recommendation",
            ],
        )

        report = FactoryExecutiveDecisionReport()
        self.assertEqual(report.business_status, "APPROVED")
        self.assertEqual(report.profitability_status, "HEALTHY")
        self.assertEqual(report.delivery_status, "ON_TRACK")
        self.assertEqual(report.executive_recommendation, "")

    def test_blocked_readiness_rejects_business_decision(self):
        report = self.builder.build(
            self._profitability_report(),
            self._delivery_report(),
            self._readiness_report(readiness_status="BLOCKED"),
        )

        self.assertEqual(report.business_status, "REJECT")
        self.assertEqual(
            report.executive_recommendation,
            "Project should not enter production",
        )

    def test_low_profitability_requires_review(self):
        report = self.builder.build(
            self._profitability_report(profitability_status="LOW"),
            self._delivery_report(),
            self._readiness_report(),
        )

        self.assertEqual(report.business_status, "REVIEW")
        self.assertEqual(
            report.executive_recommendation,
            "Review profitability before production",
        )

    def test_delayed_delivery_requires_review(self):
        report = self.builder.build(
            self._profitability_report(),
            self._delivery_report(delivery_status="DELAYED"),
            self._readiness_report(),
        )

        self.assertEqual(report.business_status, "REVIEW")
        self.assertEqual(
            report.executive_recommendation,
            "Review delivery schedule before production",
        )

    def test_approved_when_signals_are_healthy(self):
        report = self.builder.build(
            self._profitability_report(profitability_status="HEALTHY"),
            self._delivery_report(delivery_status="ON_TRACK"),
            self._readiness_report(readiness_status="READY"),
        )

        self.assertEqual(report.business_status, "APPROVED")
        self.assertEqual(report.executive_recommendation, "")

    def test_builder_does_not_mutate_inputs(self):
        profitability = self._profitability_report(
            profitability_status="LOW",
            warnings=["profitability"],
        )
        delivery = self._delivery_report(
            delivery_status="DELAYED",
            notes=["delivery"],
        )
        readiness = self._readiness_report(
            readiness_status="BLOCKED",
            tags=["readiness"],
        )
        snapshots = [
            self._snapshot(profitability),
            self._snapshot(delivery),
            self._snapshot(readiness),
        ]

        self.builder.build(profitability, delivery, readiness)

        self.assertEqual(
            [
                self._snapshot(profitability),
                self._snapshot(delivery),
                self._snapshot(readiness),
            ],
            snapshots,
        )

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _profitability_report(profitability_status="HEALTHY", warnings=None):
        from cost_intelligence.profitability_report import ProfitabilityReport

        report = ProfitabilityReport(profitability_status=profitability_status)
        report.warnings = list(warnings or [])
        return report

    @staticmethod
    def _delivery_report(delivery_status="ON_TRACK", notes=None):
        from manufacturing.factory_delivery_report import FactoryDeliveryReport

        report = FactoryDeliveryReport(delivery_status=delivery_status)
        report.notes = list(notes or [])
        return report

    @staticmethod
    def _readiness_report(readiness_status="READY", tags=None):
        return SimpleNamespace(
            readiness_status=readiness_status,
            tags=list(tags or []),
        )


if __name__ == "__main__":
    unittest.main()
