import unittest
from dataclasses import dataclass


@dataclass
class _ProductionScheduleReport:
    schedule_risk_level: str = "LOW"
    warnings: list = None


@dataclass
class _FactoryBottleneckIntelligenceReport:
    severity: str = "LOW"
    impact: str = "NO_MAJOR_BOTTLENECK"
    bottleneck: str = ""
    recommendation: str = "No bottleneck detected"


class TestFactoryDecisionIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.factory_decision_intelligence_builder import (
            FactoryDecisionIntelligenceBuilder,
        )

        self.builder = FactoryDecisionIntelligenceBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_factory_decision_report(self):
        from cost_intelligence.factory_decision_report import FactoryDecisionReport

        report = self.builder.build(*self._inputs())

        self.assertIsInstance(report, FactoryDecisionReport)

    def test_builder_copies_existing_fields_and_applies_factory_signals(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                manufacturing_ready=True,
                profitability_ok=True,
                cost_risk_level="MEDIUM",
                waste_risk_level="LOW",
                nesting_risk_level="MEDIUM",
                quotation_risk_level="LOW",
                margin_status="HEALTHY_MARGIN",
                blocking_issues=["Base blocker"],
                warnings=["Base warning"],
                recommendations=["Base recommendation"],
                factory_capacity_status="OVERLOADED",
                factory_load_status="HIGH",
                factory_bottleneck="CNC",
            )
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")
        self.assertEqual(report.manufacturing_ready, True)
        self.assertEqual(report.profitability_ok, True)
        self.assertEqual(report.cost_risk_level, "MEDIUM")
        self.assertEqual(report.waste_risk_level, "LOW")
        self.assertEqual(report.nesting_risk_level, "MEDIUM")
        self.assertEqual(report.quotation_risk_level, "LOW")
        self.assertEqual(report.margin_status, "HEALTHY_MARGIN")
        self.assertEqual(report.blocking_issues, ["Base blocker"])
        self.assertEqual(report.warnings, ["Base warning"])
        self.assertEqual(report.recommendations, ["Base recommendation"])
        self.assertEqual(report.factory_capacity_status, "OVERLOADED")
        self.assertEqual(report.factory_load_status, "HIGH")
        self.assertEqual(report.factory_bottleneck, "CNC")
        self.assertEqual(report.profitability_status, "UNKNOWN")

    def test_blocked_base_decision_remains_blocked(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="BLOCKED",
                factory_capacity_status="OVERLOADED",
                factory_load_status="HIGH",
                factory_bottleneck="Assembly",
            )
        )

        self.assertEqual(report.decision_status, "BLOCKED")

    def test_blocked_base_decision_remains_blocked_with_high_schedule_risk(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="BLOCKED",
                factory_capacity_status="AVAILABLE",
                factory_load_status="LOW",
            ),
            production_schedule_report=_ProductionScheduleReport(
                schedule_risk_level="HIGH"
            ),
        )

        self.assertEqual(report.decision_status, "BLOCKED")

    def test_overloaded_capacity_requires_review(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                factory_capacity_status="OVERLOADED",
                factory_load_status="LOW",
            )
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_high_schedule_risk_requires_review(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                factory_capacity_status="AVAILABLE",
                factory_load_status="LOW",
            ),
            production_schedule_report=_ProductionScheduleReport(
                schedule_risk_level="HIGH"
            ),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_medium_schedule_risk_does_not_change_approved_decision(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                factory_capacity_status="AVAILABLE",
                factory_load_status="LOW",
            ),
            production_schedule_report=_ProductionScheduleReport(
                schedule_risk_level="MEDIUM"
            ),
        )

        self.assertEqual(report.decision_status, "APPROVED")

    def test_high_bottleneck_severity_requires_review(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                factory_capacity_status="AVAILABLE",
                factory_load_status="LOW",
            ),
            factory_bottleneck_intelligence_report=_FactoryBottleneckIntelligenceReport(
                severity="HIGH",
                impact="NO_MAJOR_BOTTLENECK",
            ),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_delivery_risk_impact_requires_review(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                factory_capacity_status="AVAILABLE",
                factory_load_status="LOW",
            ),
            factory_bottleneck_intelligence_report=_FactoryBottleneckIntelligenceReport(
                severity="LOW",
                impact="DELIVERY_RISK",
            ),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_medium_bottleneck_severity_does_not_change_approved_decision(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                factory_capacity_status="AVAILABLE",
                factory_load_status="LOW",
            ),
            factory_bottleneck_intelligence_report=_FactoryBottleneckIntelligenceReport(
                severity="MEDIUM",
                impact="CAPACITY_PRESSURE",
            ),
        )

        self.assertEqual(report.decision_status, "APPROVED")

    def test_high_load_requires_review(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                factory_capacity_status="AVAILABLE",
                factory_load_status="HIGH",
            )
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_low_profitability_requires_review(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                profitability_status="LOW",
                factory_capacity_status="AVAILABLE",
                factory_load_status="LOW",
            ),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_medium_profitability_does_not_block(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                profitability_status="MEDIUM",
                factory_capacity_status="AVAILABLE",
                factory_load_status="LOW",
            ),
        )

        self.assertEqual(report.decision_status, "APPROVED")

    def test_high_profitability_does_not_block(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                profitability_status="HIGH",
                factory_capacity_status="AVAILABLE",
                factory_load_status="LOW",
            ),
        )

        self.assertEqual(report.decision_status, "APPROVED")

    def test_capacity_and_load_defaults_preserved_when_absent(self):
        report = self.builder.build(*self._inputs())

        self.assertEqual(report.factory_capacity_status, "UNKNOWN")
        self.assertEqual(report.factory_load_status, "LOW")
        self.assertEqual(report.factory_bottleneck, "")
        self.assertEqual(report.profitability_status, "UNKNOWN")

    def test_builder_does_not_mutate_inputs(self):
        base_decision_report, factory_intelligence_report = self._inputs(
            blocking_issues=["Base blocker"],
            warnings=["Base warning"],
            recommendations=["Base recommendation"],
        )
        base_snapshot = self._snapshot(base_decision_report)
        intelligence_snapshot = self._snapshot(factory_intelligence_report)
        production_schedule_report = _ProductionScheduleReport(
            schedule_risk_level="HIGH",
            warnings=["Schedule warning"],
        )
        bottleneck_report = _FactoryBottleneckIntelligenceReport(
            severity="HIGH",
            impact="DELIVERY_RISK",
        )
        production_schedule_snapshot = self._snapshot(production_schedule_report)
        bottleneck_snapshot = self._snapshot(bottleneck_report)

        self.builder.build(
            base_decision_report,
            factory_intelligence_report,
            production_schedule_report=production_schedule_report,
            factory_bottleneck_intelligence_report=bottleneck_report,
        )

        self.assertEqual(self._snapshot(base_decision_report), base_snapshot)
        self.assertEqual(
            self._snapshot(factory_intelligence_report),
            intelligence_snapshot,
        )
        self.assertEqual(
            self._snapshot(production_schedule_report),
            production_schedule_snapshot,
        )
        self.assertEqual(self._snapshot(bottleneck_report), bottleneck_snapshot)

    def test_existing_capacity_load_profitability_precedence_still_works(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                profitability_status="LOW",
                factory_capacity_status="OVERLOADED",
                factory_load_status="HIGH",
            ),
            production_schedule_report=_ProductionScheduleReport(
                schedule_risk_level="HIGH"
            ),
            factory_bottleneck_intelligence_report=_FactoryBottleneckIntelligenceReport(
                severity="HIGH",
                impact="DELIVERY_RISK",
            ),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _inputs(
        decision_status="APPROVED",
        manufacturing_ready=True,
        profitability_ok=True,
        cost_risk_level="LOW",
        waste_risk_level="LOW",
        nesting_risk_level="LOW",
        quotation_risk_level="LOW",
        margin_status="HEALTHY_MARGIN",
        blocking_issues=None,
        warnings=None,
        recommendations=None,
        factory_capacity_status="UNKNOWN",
        factory_load_status="LOW",
        factory_bottleneck="",
        profitability_status="UNKNOWN",
    ):
        from cost_intelligence.factory_decision_report import (
            FactoryDecisionReport,
        )
        from manufacturing.factory_capacity_intelligence_report import (
            FactoryCapacityIntelligenceReport,
        )
        from manufacturing.factory_intelligence_report import (
            FactoryIntelligenceReport,
        )
        from manufacturing.factory_load_report import FactoryLoadReport

        return (
            FactoryDecisionReport(
                decision_status=decision_status,
                manufacturing_ready=manufacturing_ready,
                profitability_ok=profitability_ok,
                cost_risk_level=cost_risk_level,
                waste_risk_level=waste_risk_level,
                nesting_risk_level=nesting_risk_level,
                quotation_risk_level=quotation_risk_level,
                margin_status=margin_status,
                blocking_issues=list(blocking_issues or []),
                warnings=list(warnings or []),
                recommendations=list(recommendations or []),
                profitability_status=profitability_status,
            ),
            FactoryIntelligenceReport(
                factory_resource_report=object(),
                factory_capacity_report=FactoryCapacityIntelligenceReport(
                    status=factory_capacity_status,
                ),
                factory_load_report=FactoryLoadReport(
                    status=factory_load_status,
                    bottleneck=factory_bottleneck,
                ),
            ),
        )


if __name__ == "__main__":
    unittest.main()
