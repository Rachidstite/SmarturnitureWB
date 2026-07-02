import inspect
import unittest
from dataclasses import FrozenInstanceError

import domain.hardware_decision_rules as rules_module
from domain.hardware_decision import HardwareDecision
from domain.operational_decision import (
    OperationalDecision,
    OperationalDecisionTraceability,
)


RULE_NAMES = (
    "apply_minifix_validation_decision_rule",
    "apply_confirmat_validation_decision_rule",
    "apply_back_panel_decision_rule",
    "apply_drawer_decision_rule",
    "apply_hinge_decision_rule",
    "apply_shelf_support_decision_rule",
)


class TestHardwareDecisionRulePatternContract(unittest.TestCase):
    def _sample_decision(self) -> HardwareDecision:
        return HardwareDecision(
            decision=OperationalDecision(
                decision_id="RULE-PATTERN-001",
                traceability=OperationalDecisionTraceability(
                    source_component="hardware_decision_builder",
                    source_rule="bootstrap_minifix_rule",
                    evidence_refs=("MinifixValidationReport:VALID-1",),
                ),
                validation_messages=("warning: clearance review needed",),
            ),
        )

    def test_current_minifix_rule_exposes_single_decision_input(self):
        rule_fn = getattr(rules_module, "apply_minifix_validation_decision_rule", None)
        self.assertTrue(callable(rule_fn))
        self.assertEqual(list(inspect.signature(rule_fn).parameters), ["decision"])

    def test_current_minifix_rule_returns_hardware_decision_and_preserves_input(self):
        decision = self._sample_decision()
        rule_fn = rules_module.apply_minifix_validation_decision_rule

        result = rule_fn(decision)

        self.assertIsInstance(result, HardwareDecision)
        self.assertIsNot(result, decision)
        self.assertEqual(decision, self._sample_decision())
        with self.assertRaises(FrozenInstanceError):
            decision.manufacturing_impact_note = "mutated"

    def test_all_future_hardware_rules_if_present_must_follow_same_signature(self):
        for rule_name in RULE_NAMES:
            rule_fn = getattr(rules_module, rule_name, None)
            if rule_fn is None:
                continue
            with self.subTest(rule_name=rule_name):
                self.assertTrue(callable(rule_fn))
                self.assertEqual(list(inspect.signature(rule_fn).parameters), ["decision"])

    def test_rules_module_has_no_engine_runtime_or_external_dependency_imports(self):
        source = inspect.getsource(rules_module).lower()

        for token in (
            "manufacturing.",
            "rules_engine",
            "hardware_library",
            "cost_intelligence",
            "geometryengine",
            "scenegraph",
            "applicationservice",
            "freecad",
            "workflow",
            "pipeline",
            "recommendation_engine",
            "recommend(",
            "select_hardware",
            "calculate_cost",
        ):
            self.assertNotIn(token, source)

    def test_rules_do_not_require_rule_engine_or_new_abstractions(self):
        source = inspect.getsource(rules_module).lower()
        self.assertNotIn("class hardwaredecisionruleengine", source)
        self.assertNotIn("class semanticnormalizationengine", source)
        self.assertNotIn("adapter", source)

    def test_minifix_rule_must_use_semantic_normalization_or_be_explicitly_bootstrap(self):
        source = inspect.getsource(rules_module)
        minifix_source = inspect.getsource(rules_module.apply_minifix_validation_decision_rule)

        uses_normalizer = "normalize_hardware_decision_semantics(" in minifix_source
        explicitly_bootstrap = (
            "bootstrap" in minifix_source.lower()
            or "legacy" in minifix_source.lower()
            or "bootstrap" in source.lower()
            or "legacy" in source.lower()
        )

        self.assertTrue(
            uses_normalizer or explicitly_bootstrap,
            "Current Minifix rule must either use normalize_hardware_decision_semantics(...) "
            "or be explicitly marked as a bootstrap/legacy rule pending refit.",
        )

    def test_rules_must_not_parse_raw_validation_text_when_semantic_signals_are_available(self):
        minifix_source = inspect.getsource(rules_module.apply_minifix_validation_decision_rule)
        uses_message_parsing = (
            "validation_messages" in minifix_source
            and "lower()" in minifix_source
            and "startswith(\"MinifixValidationReport:\")" in minifix_source
        )
        uses_normalizer = "normalize_hardware_decision_semantics(" in minifix_source
        explicitly_bootstrap = (
            "bootstrap" in minifix_source.lower() or "legacy" in minifix_source.lower()
        )

        self.assertTrue(
            uses_normalizer or not uses_message_parsing or explicitly_bootstrap,
            "Direct raw-message parsing is only acceptable for a rule explicitly marked "
            "as bootstrap/legacy pending semantic-normalization refit.",
        )


if __name__ == "__main__":
    unittest.main()
