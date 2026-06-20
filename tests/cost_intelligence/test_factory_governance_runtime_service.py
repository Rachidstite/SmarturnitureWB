import inspect
import unittest


class TestFactoryGovernanceRuntimeService(unittest.TestCase):

    def _build(self, **kwargs):
        from cost_intelligence.factory_governance_policy_context import (
            FactoryGovernancePolicyContext,
        )
        from cost_intelligence.factory_governance_runtime_service import (
            FactoryGovernanceRuntimeService,
        )

        return FactoryGovernanceRuntimeService().build(
            FactoryGovernancePolicyContext(**kwargs)
        )

    def test_service_exists(self):
        from cost_intelligence.factory_governance_runtime_service import (
            FactoryGovernanceRuntimeService,
        )

        self.assertTrue(hasattr(FactoryGovernanceRuntimeService, "build"))

    def test_clean_context_maps_to_approved(self):
        report = self._build()
        self.assertEqual(report.governance_state, "APPROVED")
        self.assertEqual(report.legacy_decision_status, "APPROVED")

    def test_low_profitability_maps_to_reprice_and_review_required(self):
        report = self._build(profitability_status="LOW")
        self.assertEqual(report.governance_state, "REPRICE")
        self.assertEqual(report.legacy_decision_status, "REVIEW_REQUIRED")

    def test_overloaded_capacity_maps_to_schedule_later_and_review_required(self):
        report = self._build(capacity_status="OVERLOADED")
        self.assertEqual(report.governance_state, "SCHEDULE_LATER")
        self.assertEqual(report.legacy_decision_status, "REVIEW_REQUIRED")

    def test_blocked_readiness_maps_to_rejected_and_blocked(self):
        report = self._build(readiness_status="BLOCKED")
        self.assertEqual(report.governance_state, "REJECTED")
        self.assertEqual(report.legacy_decision_status, "BLOCKED")

    def test_high_risk_maps_to_review_required(self):
        report = self._build(risk_status="HIGH")
        self.assertEqual(report.governance_state, "REVIEW_REQUIRED")
        self.assertEqual(report.legacy_decision_status, "REVIEW_REQUIRED")

    def test_high_load_can_expose_bottleneck_specific_details(self):
        from cost_intelligence.factory_governance_policy_context import (
            FactoryGovernancePolicyContext,
        )
        from cost_intelligence.factory_governance_runtime_service import (
            FactoryGovernanceRuntimeService,
        )

        report = FactoryGovernanceRuntimeService().build(
            FactoryGovernancePolicyContext(load_status="HIGH"),
            factory_bottleneck="ASSEMBLY",
        )

        self.assertEqual(report.primary_recommendation, "Balance workload")
        self.assertEqual(
            report.manufacturing_recommendation,
            "Increase assembly capacity",
        )
        self.assertEqual(
            report.manufacturing_secondary_recommendations,
            [
                "Add assembly station",
                "Split project into smaller batches",
                "Reduce assembly minutes per panel",
            ],
        )

    def test_over_capacity_can_expose_bottleneck_specific_details(self):
        from cost_intelligence.factory_governance_policy_context import (
            FactoryGovernancePolicyContext,
        )
        from cost_intelligence.factory_governance_runtime_service import (
            FactoryGovernanceRuntimeService,
        )

        report = FactoryGovernanceRuntimeService().build(
            FactoryGovernancePolicyContext(capacity_status="OVERLOADED"),
            factory_bottleneck="ASSEMBLY",
        )

        self.assertEqual(report.primary_recommendation, "Delay production start")
        self.assertEqual(
            report.manufacturing_recommendation,
            "Increase assembly capacity",
        )
        self.assertEqual(
            report.manufacturing_secondary_recommendations,
            [
                "Add assembly station",
                "Split project into smaller batches",
                "Reduce assembly minutes per panel",
            ],
        )

    def test_no_legacy_builder_imports(self):
        from cost_intelligence import factory_governance_runtime_service

        source = inspect.getsource(factory_governance_runtime_service)
        forbidden = [
            "FactoryDecisionBuilder",
            "ProductionReadinessBuilder",
            "FactoryDecisionIntelligenceBuilder",
            "ManufacturingExecutiveReportBuilder",
        ]
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, source)

    def test_existing_builders_are_not_modified_via_runtime_service(self):
        from cost_intelligence.factory_decision_builder import FactoryDecisionBuilder
        from cost_intelligence.factory_decision_intelligence_builder import (
            FactoryDecisionIntelligenceBuilder,
        )
        from cost_intelligence.production_readiness_builder import (
            ProductionReadinessBuilder,
        )

        self.assertNotIn(
            "FactoryGovernanceRuntimeService",
            inspect.getsource(FactoryDecisionBuilder),
        )
        self.assertNotIn(
            "FactoryGovernanceRuntimeService",
            inspect.getsource(FactoryDecisionIntelligenceBuilder),
        )
        self.assertNotIn(
            "FactoryGovernanceRuntimeService",
            inspect.getsource(ProductionReadinessBuilder),
        )
