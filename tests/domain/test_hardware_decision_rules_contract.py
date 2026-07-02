import inspect
import unittest
from dataclasses import FrozenInstanceError, replace

import domain.hardware_decision_rules as rules_module
from domain.hardware_decision import HardwareCompatibilityStatus, HardwareDecision
from domain.operational_decision import (
    OperationalDecision,
    OperationalDecisionTraceability,
)


class TestHardwareDecisionRulesContract(unittest.TestCase):
    def _base_decision(self) -> HardwareDecision:
        return HardwareDecision(
            decision=OperationalDecision(
                decision_id="HW-RULE-001",
                traceability=OperationalDecisionTraceability(
                    source_component="hardware_decision_builder",
                    source_rule="minifix_validation_evidence",
                    evidence_refs=("MinifixValidationReport:VALID-1",),
                ),
                validation_messages=(
                    "blocking clearance warning",
                    "invalid fastener spacing",
                ),
            ),
            selected_hardware_sku="",
            rejected_hardware_skus=(),
            manufacturing_impact_note="",
            quality_impact_note="",
            replacement_reason="",
        )

    def test_rule_exposes_pure_function_entrypoint(self):
        rule_fn = getattr(rules_module, "apply_minifix_validation_decision_rule", None)
        self.assertTrue(callable(rule_fn))
        self.assertEqual(
            list(inspect.signature(rule_fn).parameters),
            ["decision"],
        )

    def test_rule_is_deterministic_and_preserves_immutable_input(self):
        decision = self._base_decision()

        first = rules_module.apply_minifix_validation_decision_rule(decision)
        second = rules_module.apply_minifix_validation_decision_rule(decision)

        self.assertEqual(first, second)
        self.assertEqual(decision, self._base_decision())
        with self.assertRaises(FrozenInstanceError):
            decision.compatibility_status = HardwareCompatibilityStatus.BLOCKED

    def test_rule_returns_new_hardware_decision(self):
        decision = self._base_decision()
        result = rules_module.apply_minifix_validation_decision_rule(decision)

        self.assertIsInstance(result, HardwareDecision)
        self.assertIsNot(result, decision)

    def test_rule_reuses_minifix_validation_evidence_without_recalculating_validation(self):
        result = rules_module.apply_minifix_validation_decision_rule(self._base_decision())

        self.assertEqual(result.compatibility_status, HardwareCompatibilityStatus.BLOCKED)
        self.assertIn("blocking clearance warning", result.quality_impact_note)
        self.assertIn("invalid fastener spacing", result.quality_impact_note)
        self.assertIn("MinifixValidationReport:VALID-1", result.manufacturing_impact_note)
        self.assertIn("hardware_decision_builder", result.manufacturing_impact_note)
        self.assertIn("minifix_validation_evidence", result.manufacturing_impact_note)
        self.assertEqual(result.selected_hardware_sku, "")
        self.assertEqual(result.rejected_hardware_skus, ())

    def test_rule_may_set_needs_review_from_warning_only_evidence(self):
        decision = replace(
            self._base_decision(),
            decision=replace(
                self._base_decision().decision,
                validation_messages=("warning: review connector fit",),
            ),
        )

        result = rules_module.apply_minifix_validation_decision_rule(decision)

        self.assertEqual(
            result.compatibility_status,
            HardwareCompatibilityStatus.NEEDS_REVIEW,
        )
        self.assertIn("warning: review connector fit", result.quality_impact_note)

    def test_rule_leaves_decision_unchanged_without_minifix_validation_reference(self):
        decision = replace(
            self._base_decision(),
            decision=replace(
                self._base_decision().decision,
                traceability=replace(
                    self._base_decision().decision.traceability,
                    evidence_refs=("ConfirmatValidationReport:VALID-2",),
                ),
            ),
        )

        result = rules_module.apply_minifix_validation_decision_rule(decision)

        self.assertEqual(result, decision)
        self.assertIsNot(result, decision)

    def test_replacement_reason_remains_empty_without_explicit_replacement_evidence(self):
        result = rules_module.apply_minifix_validation_decision_rule(self._base_decision())
        self.assertEqual(result.replacement_reason, "")

    def test_rule_has_no_validator_selection_cost_or_runtime_dependencies(self):
        source = inspect.getsource(rules_module).lower()

        for token in (
            "manufacturing.",
            "rules_engine",
            "hardware_library",
            "geometryengine",
            "scenegraph",
            "applicationservice",
            "freecad",
            "recommendation_engine",
            "recommend(",
            "agent",
            "llm",
            "cost_intelligence",
            "calculate_cost",
            "select_hardware",
            "reject_hardware",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
