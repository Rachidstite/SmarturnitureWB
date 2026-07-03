import inspect
from types import SimpleNamespace
import unittest


class TestFactoryGovernanceRecommendationBuilder(unittest.TestCase):

    def _build(
        self,
        policy_kwargs=None,
        authority_kwargs=None,
        management_status_source=None,
    ):
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
            management_status_source=management_status_source,
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

    def test_management_status_recommendations_are_deterministic(self):
        report = self._build(
            {"reason_code": "POLICY_CLEAR"},
            {"winning_signal": "POLICY_CLEAR"},
            management_status_source=SimpleNamespace(
                project_profitability_status="LOW",
                material_efficiency_status="STABLE",
                waste_risk_status="HIGH",
                bottleneck_status="HIGH",
                production_readiness_status="READY_WITH_WARNINGS",
                overall_management_status="MONITOR",
            ),
        )

        self.assertEqual(
            report.primary_recommendation,
            "Delay production release until readiness issues are cleared",
        )
        self.assertEqual(report.urgency, "HIGH")
        self.assertEqual(
            report.secondary_recommendations,
            [
                "Review quotation pricing",
                "Reschedule production around bottlenecks",
                "Review nesting and material usage",
                "Review material efficiency before release",
            ],
        )

    def test_management_status_recommendations_extend_existing_signal_without_replacing_it(self):
        report = self._build(
            {"reason_code": "LOW_MARGIN"},
            {"winning_signal": "LOW_MARGIN"},
            management_status_source=SimpleNamespace(
                project_profitability_status="LOW",
                material_efficiency_status="STABLE",
                waste_risk_status="HIGH",
                bottleneck_status="UNKNOWN",
                production_readiness_status="READY",
                overall_management_status="MONITOR",
            ),
        )

        self.assertEqual(report.primary_recommendation, "Increase quotation price")
        self.assertEqual(
            report.secondary_recommendations,
            [
                "Reduce material waste",
                "Review hardware selection",
                "Review quotation pricing",
                "Review nesting and material usage",
                "Review material efficiency before release",
            ],
        )

    def test_highest_priority_management_status_becomes_primary(self):
        report = self._build(
            {"reason_code": "POLICY_CLEAR"},
            {"winning_signal": "POLICY_CLEAR"},
            management_status_source=SimpleNamespace(
                project_profitability_status="LOW",
                material_efficiency_status="STABLE",
                waste_risk_status="HIGH",
                bottleneck_status="HIGH",
                production_readiness_status="BLOCKED",
                overall_management_status="ACTION_REQUIRED",
            ),
        )

        self.assertEqual(
            report.primary_recommendation,
            "Delay production release until readiness issues are cleared",
        )

    def test_duplicate_recommendations_are_removed(self):
        from cost_intelligence.factory_governance_recommendation_builder import (
            FactoryGovernanceRecommendationBuilder,
        )

        deduped = FactoryGovernanceRecommendationBuilder._dedupe_recommendations(
            [
                "Review quotation pricing",
                "Review quotation pricing",
                "Review nesting and material usage",
                "Review nesting and material usage",
            ]
        )

        self.assertEqual(
            deduped,
            [
                "Review quotation pricing",
                "Review nesting and material usage",
            ],
        )

    def test_builder_reuses_status_fields_without_recomputing_kpis(self):
        from cost_intelligence.factory_governance_recommendation_builder import (
            FactoryGovernanceRecommendationBuilder,
        )

        source = inspect.getsource(FactoryGovernanceRecommendationBuilder)
        for helper_name in (
            "_profitability_status",
            "_material_efficiency_status",
            "_waste_risk_status",
            "_overall_management_status",
        ):
            self.assertFalse(
                hasattr(FactoryGovernanceRecommendationBuilder, helper_name)
            )

        self.assertIn("_build_management_recommendations(", source)
        for field_name in (
            '"project_profitability_status"',
            '"material_efficiency_status"',
            '"waste_risk_status"',
            '"bottleneck_status"',
            '"production_readiness_status"',
        ):
            self.assertIn(field_name, source)

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
