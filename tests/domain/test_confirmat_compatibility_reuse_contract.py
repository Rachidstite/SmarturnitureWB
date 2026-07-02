import inspect
import unittest
from dataclasses import FrozenInstanceError

import domain.compatibility_decision_rule as compatibility_module
import domain.hardware_decision_rules as rules_module
from domain.hardware_decision import HardwareCompatibilityStatus, HardwareDecision
from domain.operational_decision import (
    OperationalDecision,
    OperationalDecisionTraceability,
)


class TestConfirmatCompatibilityReuseContract(unittest.TestCase):
    def _decision_with_evidence(self, evidence_ref: str, messages: tuple[str, ...]) -> HardwareDecision:
        return HardwareDecision(
            decision=OperationalDecision(
                decision_id="CONFIRMAT-COMPAT-001",
                traceability=OperationalDecisionTraceability(
                    source_component="hardware_decision_builder",
                    source_rule="compatibility_validation_evidence",
                    evidence_refs=(evidence_ref,),
                ),
                validation_messages=messages,
            ),
            manufacturing_impact_note="",
            quality_impact_note="",
            replacement_reason="",
        )

    def test_confirmat_evidence_uses_generic_compatibility_rule(self):
        rule_fn = getattr(compatibility_module, "apply_compatibility_decision_rule", None)
        self.assertTrue(callable(rule_fn))

        result = rule_fn(
            self._decision_with_evidence(
                "ConfirmatValidationReport:VALID-1",
                ("warning: review edge distance",),
            )
        )

        self.assertIsInstance(result, HardwareDecision)

    def test_no_confirmat_specific_rule_is_required(self):
        self.assertIsNone(
            getattr(rules_module, "apply_confirmat_validation_decision_rule", None)
        )
        self.assertIsNone(
            getattr(compatibility_module, "apply_confirmat_validation_decision_rule", None)
        )

    def test_confirmat_blocked_or_invalid_signal_produces_blocked(self):
        result = compatibility_module.apply_compatibility_decision_rule(
            self._decision_with_evidence(
                "ConfirmatValidationReport:VALID-2",
                ("blocking edge distance failure", "invalid connector spacing"),
            )
        )

        self.assertEqual(result.compatibility_status, HardwareCompatibilityStatus.BLOCKED)

    def test_confirmat_warning_review_or_risk_signal_produces_needs_review(self):
        for messages in (
            ("warning: review edge distance",),
            ("review connector fit",),
            ("risk observed in fastener spacing",),
        ):
            with self.subTest(messages=messages):
                result = compatibility_module.apply_compatibility_decision_rule(
                    self._decision_with_evidence(
                        "ConfirmatValidationReport:VALID-3",
                        messages,
                    )
                )
                self.assertEqual(
                    result.compatibility_status,
                    HardwareCompatibilityStatus.NEEDS_REVIEW,
                )

    def test_confirmat_valid_or_pass_signal_must_not_block_decision(self):
        for messages in (
            (),
            ("valid",),
            ("pass",),
        ):
            with self.subTest(messages=messages):
                result = compatibility_module.apply_compatibility_decision_rule(
                    self._decision_with_evidence(
                        "ConfirmatValidationReport:VALID-4",
                        messages,
                    )
                )
                self.assertNotEqual(
                    result.compatibility_status,
                    HardwareCompatibilityStatus.BLOCKED,
                )

    def test_identical_semantic_signals_from_minifix_and_confirmat_produce_equivalent_outcomes(self):
        minifix = compatibility_module.apply_compatibility_decision_rule(
            self._decision_with_evidence(
                "MinifixValidationReport:VALID-5",
                ("warning: review connector fit",),
            )
        )
        confirmat = compatibility_module.apply_compatibility_decision_rule(
            self._decision_with_evidence(
                "ConfirmatValidationReport:VALID-5",
                ("warning: review connector fit",),
            )
        )

        self.assertEqual(minifix.compatibility_status, confirmat.compatibility_status)
        self.assertEqual(minifix.quality_impact_note, confirmat.quality_impact_note)

    def test_rule_has_no_hardware_specific_branching_or_external_dependencies(self):
        source = inspect.getsource(compatibility_module).lower()

        for token in (
            "manufacturing.",
            "rules_engine",
            "hardware_library",
            "cost_intelligence",
            "geometryengine",
            "scenegraph",
            "applicationservice",
            "freecad",
            "startswith(\"confirmat",
            "== \"confirmatvalidationreport\"",
            "select_hardware",
            "reject_hardware",
            "calculate_cost",
            "recommend(",
        ):
            self.assertNotIn(token, source)

    def test_rule_preserves_immutable_input(self):
        decision = self._decision_with_evidence(
            "ConfirmatValidationReport:VALID-6",
            ("warning: review edge distance",),
        )

        result = compatibility_module.apply_compatibility_decision_rule(decision)

        self.assertIsNot(result, decision)
        self.assertEqual(
            decision,
            self._decision_with_evidence(
                "ConfirmatValidationReport:VALID-6",
                ("warning: review edge distance",),
            ),
        )
        with self.assertRaises(FrozenInstanceError):
            decision.compatibility_status = HardwareCompatibilityStatus.BLOCKED


if __name__ == "__main__":
    unittest.main()
