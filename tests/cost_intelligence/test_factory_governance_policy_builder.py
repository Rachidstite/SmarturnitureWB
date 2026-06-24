import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestFactoryGovernancePolicyBuilder(unittest.TestCase):

    def test_builder_exists_and_returns_report(self):
        from cost_intelligence.factory_governance_policy_builder import (
            FactoryGovernancePolicyBuilder,
        )
        from cost_intelligence.factory_governance_policy_report import (
            FactoryGovernancePolicyReport,
        )

        self.assertTrue(hasattr(FactoryGovernancePolicyBuilder, "build"))
        report = FactoryGovernancePolicyBuilder().build(self._context())
        self.assertIsInstance(report, FactoryGovernancePolicyReport)

    def test_report_is_dataclass_with_independent_default_lists(self):
        from cost_intelligence.factory_governance_policy_report import (
            FactoryGovernancePolicyReport,
        )

        self.assertTrue(is_dataclass(FactoryGovernancePolicyReport))
        self.assertEqual(
            [field.name for field in fields(FactoryGovernancePolicyReport)],
            [
                "governance_state",
                "dominant_authority",
                "reason_code",
                "explanation",
                "recommendations",
                "warnings",
            ],
        )

        first = FactoryGovernancePolicyReport()
        second = FactoryGovernancePolicyReport()

        self.assertIsNot(first.recommendations, second.recommendations)
        self.assertIsNot(first.warnings, second.warnings)

        first.recommendations.append("Review")
        first.warnings.append("Warning")

        self.assertEqual(second.recommendations, [])
        self.assertEqual(second.warnings, [])

    def test_precedence_order_matches_existing_policy_contract(self):
        cases = [
            (
                {"readiness_status": "BLOCKED", "profitability_status": "LOW"},
                "REJECTED",
                "ProductionReadinessBuilder",
                "READINESS_BLOCKED",
            ),
            (
                {"profitability_status": "LOW", "capacity_status": "OVERLOADED"},
                "REPRICE",
                "ProfitabilityCalculator",
                "LOW_MARGIN",
            ),
            (
                {"capacity_status": "OVERLOADED", "load_status": "HIGH"},
                "SCHEDULE_LATER",
                "FactoryCapacityIntelligenceBuilder",
                "OVER_CAPACITY",
            ),
            (
                {"load_status": "HIGH", "risk_status": "HIGH"},
                "SCHEDULE_LATER",
                "FactoryLoadBuilder",
                "HIGH_LOAD",
            ),
            (
                {"risk_status": "HIGH"},
                "REVIEW_REQUIRED",
                "FactoryDecisionBuilder",
                "HIGH_RISK",
            ),
            (
                {},
                "APPROVED",
                "FactoryGovernancePolicyBuilder",
                "POLICY_CLEAR",
            ),
        ]

        for kwargs, governance_state, dominant_authority, reason_code in cases:
            with self.subTest(kwargs=kwargs):
                report = self._build(**kwargs)
                self.assertEqual(report.governance_state, governance_state)
                self.assertEqual(report.dominant_authority, dominant_authority)
                self.assertEqual(report.reason_code, reason_code)

    def test_higher_priority_signal_wins_when_multiple_signals_are_active(self):
        report = self._build(
            readiness_status="BLOCKED",
            profitability_status="LOW",
            capacity_status="OVERLOADED",
            load_status="HIGH",
            risk_status="HIGH",
        )

        self.assertEqual(report.governance_state, "REJECTED")
        self.assertEqual(report.dominant_authority, "ProductionReadinessBuilder")
        self.assertEqual(report.reason_code, "READINESS_BLOCKED")
        self.assertEqual(report.explanation, "Readiness gate is blocked.")

        report = self._build(
            profitability_status="LOW",
            capacity_status="OVERLOADED",
            load_status="HIGH",
            risk_status="HIGH",
        )

        self.assertEqual(report.governance_state, "REPRICE")
        self.assertEqual(report.dominant_authority, "ProfitabilityCalculator")
        self.assertEqual(report.reason_code, "LOW_MARGIN")

        report = self._build(
            capacity_status="OVERLOADED",
            load_status="HIGH",
            risk_status="HIGH",
        )

        self.assertEqual(report.governance_state, "SCHEDULE_LATER")
        self.assertEqual(
            report.dominant_authority,
            "FactoryCapacityIntelligenceBuilder",
        )
        self.assertEqual(report.reason_code, "OVER_CAPACITY")

    def test_context_is_not_mutated(self):
        context = self._context(
            readiness_status="BLOCKED",
            profitability_status="LOW",
            capacity_status="OVERLOADED",
            load_status="HIGH",
            risk_status="HIGH",
        )
        original = self._snapshot(context)

        self._build_context(context)

        self.assertEqual(self._snapshot(context), original)

    def test_no_forbidden_runtime_or_pipeline_imports(self):
        from cost_intelligence import factory_governance_policy_builder

        source = inspect.getsource(factory_governance_policy_builder)
        forbidden_tokens = [
            "factory_governance_runtime_service",
            "factory_decision_builder",
            "production_readiness_builder",
            "factory_decision_intelligence_builder",
            "manufacturing_executive_report_builder",
            "ManufacturingCommercialPipelineBuilder",
            "ManufacturingOptimizationPipelineBuilder",
        ]
        for token in forbidden_tokens:
            with self.subTest(token=token):
                self.assertNotIn(token, source)

    def _build(self, **kwargs):
        from cost_intelligence.factory_governance_policy_builder import (
            FactoryGovernancePolicyBuilder,
        )

        return FactoryGovernancePolicyBuilder().build(self._context(**kwargs))

    @staticmethod
    def _build_context(context):
        from cost_intelligence.factory_governance_policy_builder import (
            FactoryGovernancePolicyBuilder,
        )

        return FactoryGovernancePolicyBuilder().build(context)

    @staticmethod
    def _context(**kwargs):
        from cost_intelligence.factory_governance_policy_context import (
            FactoryGovernancePolicyContext,
        )

        return FactoryGovernancePolicyContext(**kwargs)

    @staticmethod
    def _snapshot(context):
        return dict(context.__dict__)


if __name__ == "__main__":
    unittest.main()
