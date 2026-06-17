import unittest


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

    def test_overloaded_capacity_requires_review(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                factory_capacity_status="OVERLOADED",
                factory_load_status="LOW",
            )
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_high_load_requires_review(self):
        report = self.builder.build(
            *self._inputs(
                decision_status="APPROVED",
                factory_capacity_status="AVAILABLE",
                factory_load_status="HIGH",
            )
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_capacity_and_load_defaults_preserved_when_absent(self):
        report = self.builder.build(*self._inputs())

        self.assertEqual(report.factory_capacity_status, "UNKNOWN")
        self.assertEqual(report.factory_load_status, "LOW")
        self.assertEqual(report.factory_bottleneck, "")

    def test_builder_does_not_mutate_inputs(self):
        base_decision_report, factory_intelligence_report = self._inputs(
            blocking_issues=["Base blocker"],
            warnings=["Base warning"],
            recommendations=["Base recommendation"],
        )
        base_snapshot = self._snapshot(base_decision_report)
        intelligence_snapshot = self._snapshot(factory_intelligence_report)

        self.builder.build(base_decision_report, factory_intelligence_report)

        self.assertEqual(self._snapshot(base_decision_report), base_snapshot)
        self.assertEqual(
            self._snapshot(factory_intelligence_report),
            intelligence_snapshot,
        )

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
