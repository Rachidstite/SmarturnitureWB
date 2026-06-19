import inspect
import unittest


class TestLegacyThreeStateAdapter(unittest.TestCase):
    def test_every_governance_state_maps_correctly(self):
        from cost_intelligence.factory_governance_state import (
            FactoryGovernanceState,
        )
        from cost_intelligence.legacy_three_state_adapter import (
            LegacyThreeStateAdapter,
        )

        adapter = LegacyThreeStateAdapter()
        expected = {
            FactoryGovernanceState.APPROVED: "APPROVED",
            FactoryGovernanceState.REPRICE: "REVIEW_REQUIRED",
            FactoryGovernanceState.SCHEDULE_LATER: "REVIEW_REQUIRED",
            FactoryGovernanceState.REVIEW_REQUIRED: "REVIEW_REQUIRED",
            FactoryGovernanceState.REJECTED: "BLOCKED",
        }
        for state, legacy_state in expected.items():
            with self.subTest(state=state):
                self.assertEqual(adapter.adapt(state), legacy_state)

    def test_unknown_states_raise_value_error(self):
        from cost_intelligence.legacy_three_state_adapter import (
            LegacyThreeStateAdapter,
        )

        adapter = LegacyThreeStateAdapter()
        for invalid_state in ("", "UNKNOWN", object()):
            with self.subTest(invalid_state=invalid_state):
                with self.assertRaises(ValueError):
                    adapter.adapt(invalid_state)

    def test_adapter_has_no_runtime_builder_imports(self):
        from cost_intelligence import legacy_three_state_adapter

        source = inspect.getsource(legacy_three_state_adapter)
        forbidden_imports = [
            "from cost_intelligence.factory_decision_builder import",
            "from cost_intelligence.production_readiness_builder import",
            "from cost_intelligence.factory_decision_intelligence_builder import",
            "from cost_intelligence.manufacturing_executive_report_builder import",
        ]
        for token in forbidden_imports:
            with self.subTest(token=token):
                self.assertNotIn(token, source)

    def test_existing_builders_remain_untouched(self):
        from cost_intelligence.factory_decision_builder import (
            FactoryDecisionBuilder,
        )
        from cost_intelligence.factory_decision_intelligence_builder import (
            FactoryDecisionIntelligenceBuilder,
        )
        from cost_intelligence.production_readiness_builder import (
            ProductionReadinessBuilder,
        )

        self.assertNotIn(
            "LegacyThreeStateAdapter",
            inspect.getsource(FactoryDecisionBuilder),
        )
        self.assertNotIn(
            "LegacyThreeStateAdapter",
            inspect.getsource(FactoryDecisionIntelligenceBuilder),
        )
        self.assertNotIn(
            "LegacyThreeStateAdapter",
            inspect.getsource(ProductionReadinessBuilder),
        )

    def test_adapter_is_deterministic(self):
        from cost_intelligence.factory_governance_state import (
            FactoryGovernanceState,
        )
        from cost_intelligence.legacy_three_state_adapter import (
            LegacyThreeStateAdapter,
        )

        adapter = LegacyThreeStateAdapter()
        for state in FactoryGovernanceState:
            with self.subTest(state=state):
                first = adapter.adapt(state)
                second = adapter.adapt(state)
                self.assertEqual(first, second)
