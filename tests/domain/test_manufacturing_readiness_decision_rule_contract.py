import inspect
import unittest
from dataclasses import FrozenInstanceError

import domain.manufacturing_readiness_decision_rule as readiness_module
from domain.hardware_decision import HardwareCompatibilityStatus, HardwareDecision
from domain.operational_decision import (
    OperationalDecision,
    OperationalDecisionTraceability,
)


class TestManufacturingReadinessDecisionRuleContract(unittest.TestCase):
    def _decision_with_evidence(self, evidence_ref: str, messages: tuple[str, ...]) -> HardwareDecision:
        return HardwareDecision(
            decision=OperationalDecision(
                decision_id="READINESS-001",
                traceability=OperationalDecisionTraceability(
                    source_component="hardware_decision_builder",
                    source_rule="manufacturing_readiness_evidence",
                    evidence_refs=(evidence_ref,),
                ),
                validation_messages=messages,
            ),
            manufacturing_impact_note="",
        )

    def test_rule_exposes_pure_function_entrypoint(self):
        rule_fn = getattr(readiness_module, "apply_manufacturing_readiness_decision_rule", None)
        self.assertTrue(callable(rule_fn))
        self.assertEqual(list(inspect.signature(rule_fn).parameters), ["decision"])

    def test_rule_preserves_immutable_input_and_returns_new_decision(self):
        decision = self._decision_with_evidence(
            "BackPanelDecisionReport:BACK-1",
            ("blocking manufacturing issue",),
        )
        result = readiness_module.apply_manufacturing_readiness_decision_rule(decision)

        self.assertIsInstance(result, HardwareDecision)
        self.assertIsNot(result, decision)
        self.assertEqual(
            decision,
            self._decision_with_evidence(
                "BackPanelDecisionReport:BACK-1",
                ("blocking manufacturing issue",),
            ),
        )
        with self.assertRaises(FrozenInstanceError):
            decision.manufacturing_impact_note = "mutated"

    def test_rule_uses_semantic_normalizer(self):
        source = inspect.getsource(readiness_module)
        self.assertIn("normalize_hardware_decision_semantics(", source)

    def test_blocked_manufacturing_evidence_updates_decision_correctly(self):
        result = readiness_module.apply_manufacturing_readiness_decision_rule(
            self._decision_with_evidence(
                "BackPanelDecisionReport:BACK-2",
                ("blocked manufacturing path",),
            )
        )

        self.assertEqual(result.compatibility_status, HardwareCompatibilityStatus.BLOCKED)
        self.assertIn("Manufacturing readiness: BLOCKED", result.manufacturing_impact_note)

    def test_needs_review_manufacturing_evidence_updates_note_without_forcing_block(self):
        decision = self._decision_with_evidence(
            "DrawerDecisionReport:DRAWER-1",
            ("warning: manufacturing review required",),
        )
        result = readiness_module.apply_manufacturing_readiness_decision_rule(decision)

        self.assertNotEqual(result.compatibility_status, HardwareCompatibilityStatus.BLOCKED)
        self.assertIn("Manufacturing readiness: WARNING", result.manufacturing_impact_note)

    def test_valid_manufacturing_evidence_does_not_block(self):
        result = readiness_module.apply_manufacturing_readiness_decision_rule(
            self._decision_with_evidence(
                "ManufacturingValidationReport:VALID-1",
                (),
            )
        )

        self.assertNotEqual(result.compatibility_status, HardwareCompatibilityStatus.BLOCKED)

    def test_evidence_source_name_does_not_affect_behaviour(self):
        back_panel = readiness_module.apply_manufacturing_readiness_decision_rule(
            self._decision_with_evidence(
                "BackPanelDecisionReport:BACK-3",
                ("warning: manufacturing review required",),
            )
        )
        drawer = readiness_module.apply_manufacturing_readiness_decision_rule(
            self._decision_with_evidence(
                "DrawerDecisionReport:DRAWER-3",
                ("warning: manufacturing review required",),
            )
        )

        self.assertEqual(back_panel.compatibility_status, drawer.compatibility_status)
        self.assertEqual(back_panel.manufacturing_impact_note, drawer.manufacturing_impact_note)

    def test_rule_has_no_manufacturing_imports_or_report_specific_branching(self):
        source = inspect.getsource(readiness_module).lower()

        for token in (
            "manufacturing.",
            "rules_engine",
            "hardware_library",
            "cost_intelligence",
            "geometryengine",
            "scenegraph",
            "applicationservice",
            "freecad",
            "adapter",
            "startswith(\"backpanel",
            "startswith(\"drawer",
            "select_hardware",
            "calculate_cost",
            "recommend(",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
