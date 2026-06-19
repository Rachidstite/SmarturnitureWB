import inspect
import unittest


class TestFactoryGovernanceAuthorityResolver(unittest.TestCase):

    def _resolve(self, **kwargs):
        from cost_intelligence.factory_governance_authority_resolver import (
            FactoryGovernanceAuthorityResolver,
        )
        from cost_intelligence.factory_governance_policy_context import (
            FactoryGovernancePolicyContext,
        )

        context = FactoryGovernancePolicyContext(**kwargs)
        return FactoryGovernanceAuthorityResolver().resolve(context)

    def test_resolver_exists_and_returns_authority_report(self):
        from cost_intelligence.factory_governance_authority_report import (
            FactoryGovernanceAuthorityReport,
        )
        from cost_intelligence.factory_governance_authority_resolver import (
            FactoryGovernanceAuthorityResolver,
        )

        self.assertTrue(hasattr(FactoryGovernanceAuthorityResolver, "resolve"))
        report = self._resolve()
        self.assertIsInstance(report, FactoryGovernanceAuthorityReport)

    def test_precedence_order_and_winning_signal(self):
        cases = [
            (
                {"readiness_status": "BLOCKED", "profitability_status": "LOW"},
                ("ProductionReadinessBuilder", 1, "READINESS_BLOCKED"),
            ),
            (
                {"profitability_status": "LOW", "capacity_status": "OVERLOADED"},
                ("ProfitabilityCalculator", 2, "LOW_MARGIN"),
            ),
            (
                {"capacity_status": "OVERLOADED", "load_status": "HIGH"},
                ("FactoryCapacityIntelligenceBuilder", 3, "OVER_CAPACITY"),
            ),
            (
                {"load_status": "HIGH", "risk_status": "HIGH"},
                ("FactoryLoadBuilder", 4, "HIGH_LOAD"),
            ),
            (
                {"risk_status": "HIGH"},
                ("FactoryDecisionBuilder", 5, "HIGH_RISK"),
            ),
            (
                {},
                ("FactoryGovernancePolicyBuilder", 6, "POLICY_CLEAR"),
            ),
        ]

        for kwargs, expected in cases:
            with self.subTest(kwargs=kwargs):
                report = self._resolve(**kwargs)
                self.assertEqual(
                    (
                        report.authority_owner,
                        report.authority_rank,
                        report.winning_signal,
                    ),
                    expected,
                )

    def test_losing_signals_capture_lower_priority_active_signals(self):
        blocked = self._resolve(
            readiness_status="BLOCKED",
            profitability_status="LOW",
            capacity_status="OVERLOADED",
            load_status="HIGH",
            risk_status="HIGH",
        )
        self.assertIn("LOW_MARGIN", blocked.losing_signals)
        self.assertIn("OVER_CAPACITY", blocked.losing_signals)
        self.assertIn("HIGH_LOAD", blocked.losing_signals)
        self.assertIn("HIGH_RISK", blocked.losing_signals)

        low_profit = self._resolve(
            profitability_status="LOW",
            capacity_status="OVERLOADED",
            load_status="HIGH",
            risk_status="HIGH",
        )
        self.assertNotIn("READINESS_BLOCKED", low_profit.losing_signals)
        self.assertIn("OVER_CAPACITY", low_profit.losing_signals)
        self.assertIn("HIGH_LOAD", low_profit.losing_signals)
        self.assertIn("HIGH_RISK", low_profit.losing_signals)

    def test_unknown_context_keeps_policy_clear(self):
        report = self._resolve()
        self.assertEqual(report.authority_owner, "FactoryGovernancePolicyBuilder")
        self.assertEqual(report.authority_rank, 6)
        self.assertEqual(report.winning_signal, "POLICY_CLEAR")

    def test_no_forbidden_builder_imports(self):
        from cost_intelligence import factory_governance_authority_resolver

        source = inspect.getsource(factory_governance_authority_resolver)
        forbidden_imports = [
            "from cost_intelligence.factory_decision_builder import",
            "from cost_intelligence.production_readiness_builder import",
            "from cost_intelligence.factory_decision_intelligence_builder import",
            "from cost_intelligence.manufacturing_executive_report_builder import",
        ]
        for token in forbidden_imports:
            with self.subTest(token=token):
                self.assertNotIn(token, source)

    def test_existing_legacy_builders_remain_untouched(self):
        from cost_intelligence.factory_decision_builder import FactoryDecisionBuilder
        from cost_intelligence.factory_decision_intelligence_builder import (
            FactoryDecisionIntelligenceBuilder,
        )
        from cost_intelligence.production_readiness_builder import (
            ProductionReadinessBuilder,
        )

        self.assertNotIn(
            "FactoryGovernanceAuthorityResolver",
            inspect.getsource(FactoryDecisionBuilder),
        )
        self.assertNotIn(
            "FactoryGovernanceAuthorityResolver",
            inspect.getsource(FactoryDecisionIntelligenceBuilder),
        )
        self.assertNotIn(
            "FactoryGovernanceAuthorityResolver",
            inspect.getsource(ProductionReadinessBuilder),
        )
