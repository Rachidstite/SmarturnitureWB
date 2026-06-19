import inspect
import unittest


class TestFactoryGovernanceRecommendationBuilder(unittest.TestCase):

    def _build(self, policy_kwargs=None, authority_kwargs=None):
        from cost_intelligence.factory_governance_authority_report import (
            FactoryGovernanceAuthorityReport,
        )
        from cost_intelligence.factory_governance_policy_report import (
            FactoryGovernancePolicyReport,
        )
        from cost_intelligence.factory_governance_recommendation_builder import (
            FactoryGovernanceRecommendationBuilder,
        )

        policy_kwargs = policy_kwargs or {}
        authority_kwargs = authority_kwargs or {}
        policy_report = FactoryGovernancePolicyReport(**policy_kwargs)
        authority_report = FactoryGovernanceAuthorityReport(**authority_kwargs)
        return FactoryGovernanceRecommendationBuilder().build(
            policy_report,
            authority_report,
        )

    def test_builder_exists(self):
        from cost_intelligence.factory_governance_recommendation_builder import (
            FactoryGovernanceRecommendationBuilder,
        )

        self.assertTrue(hasattr(FactoryGovernanceRecommendationBuilder, "build"))

    def test_safe_defaults(self):
        from cost_intelligence.factory_governance_recommendation_report import (
            FactoryGovernanceRecommendationReport,
        )

        report = FactoryGovernanceRecommendationReport()
        self.assertEqual(report.primary_recommendation, "")
        self.assertEqual(report.secondary_recommendations, [])
        self.assertEqual(report.urgency, "")
        self.assertEqual(report.business_impact, "")
        self.assertEqual(report.expected_outcome, "")
        self.assertEqual(report.warnings, [])

    def test_every_winning_signal_generates_a_recommendation(self):
        cases = [
            (
                {"reason_code": "READINESS_BLOCKED"},
                {"winning_signal": "READINESS_BLOCKED"},
                (
                    "Review manufacturing constraints",
                    "HIGH",
                    "Blocking production release until readiness issues are cleared",
                    ["Review joinery validation", "Review collision validation"],
                ),
            ),
            (
                {"reason_code": "LOW_MARGIN"},
                {"winning_signal": "LOW_MARGIN"},
                (
                    "Increase quotation price",
                    "HIGH",
                    "Commercial terms are weak and need repricing",
                    ["Reduce material waste", "Review hardware selection"],
                ),
            ),
            (
                {"reason_code": "OVER_CAPACITY"},
                {"winning_signal": "OVER_CAPACITY"},
                (
                    "Delay production start",
                    "MEDIUM",
                    "Factory capacity must clear before release",
                    ["Reschedule workload", "Increase production window"],
                ),
            ),
            (
                {"reason_code": "HIGH_LOAD"},
                {"winning_signal": "HIGH_LOAD"},
                (
                    "Balance workload",
                    "MEDIUM",
                    "Production load should be redistributed",
                    ["Reassign production resources"],
                ),
            ),
            (
                {"reason_code": "HIGH_RISK"},
                {"winning_signal": "HIGH_RISK"},
                (
                    "Manual engineering review",
                    "HIGH",
                    "High-risk jobs require feasibility review",
                    ["Review manufacturing feasibility"],
                ),
            ),
            (
                {"reason_code": "POLICY_CLEAR"},
                {"winning_signal": "POLICY_CLEAR"},
                (
                    "Proceed with production",
                    "LOW",
                    "Job is ready for execution",
                    [],
                ),
            ),
        ]

        for policy_kwargs, authority_kwargs, expected in cases:
            with self.subTest(winning_signal=authority_kwargs["winning_signal"]):
                report = self._build(policy_kwargs, authority_kwargs)
                self.assertEqual(
                    (
                        report.primary_recommendation,
                        report.urgency,
                        report.business_impact,
                        report.secondary_recommendations,
                    ),
                    expected,
                )

    def test_no_legacy_builder_imports(self):
        from cost_intelligence import factory_governance_recommendation_builder

        source = inspect.getsource(factory_governance_recommendation_builder)
        forbidden = [
            "FactoryDecisionBuilder",
            "ProductionReadinessBuilder",
            "FactoryDecisionIntelligenceBuilder",
            "ManufacturingExecutiveReportBuilder",
        ]
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, source)

    def test_existing_runtime_behavior_unchanged(self):
        from cost_intelligence.factory_decision_builder import FactoryDecisionBuilder
        from cost_intelligence.factory_decision_intelligence_builder import (
            FactoryDecisionIntelligenceBuilder,
        )
        from cost_intelligence.production_readiness_builder import (
            ProductionReadinessBuilder,
        )

        self.assertNotIn(
            "FactoryGovernanceRecommendationBuilder",
            inspect.getsource(FactoryDecisionBuilder),
        )
        self.assertNotIn(
            "FactoryGovernanceRecommendationBuilder",
            inspect.getsource(FactoryDecisionIntelligenceBuilder),
        )
        self.assertNotIn(
            "FactoryGovernanceRecommendationBuilder",
            inspect.getsource(ProductionReadinessBuilder),
        )
