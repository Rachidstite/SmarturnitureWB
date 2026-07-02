import inspect
import unittest
from dataclasses import FrozenInstanceError, replace

import domain.compatibility_decision_rule as compatibility_module
from domain.hardware_decision import HardwareCompatibilityStatus, HardwareDecision
from domain.operational_decision import (
    OperationalDecision,
    OperationalDecisionTraceability,
)


class TestCompatibilityDecisionRuleContract(unittest.TestCase):
    def _decision_with_evidence(self, evidence_ref: str, messages: tuple[str, ...]) -> HardwareDecision:
        return HardwareDecision(
            decision=OperationalDecision(
                decision_id="COMPAT-001",
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

    def test_rule_exposes_pure_function_entrypoint(self):
        rule_fn = getattr(compatibility_module, "apply_compatibility_decision_rule", None)
        self.assertTrue(callable(rule_fn))
        self.assertEqual(list(inspect.signature(rule_fn).parameters), ["decision"])

    def test_rule_preserves_immutable_input_and_returns_new_decision(self):
        decision = self._decision_with_evidence(
            "MinifixValidationReport:VALID-1",
            ("blocking clearance warning",),
        )

        result = compatibility_module.apply_compatibility_decision_rule(decision)

        self.assertIsInstance(result, HardwareDecision)
        self.assertIsNot(result, decision)
        self.assertEqual(decision, self._decision_with_evidence(
            "MinifixValidationReport:VALID-1",
            ("blocking clearance warning",),
        ))
        with self.assertRaises(FrozenInstanceError):
            decision.quality_impact_note = "mutated"

    def test_rule_uses_semantic_normalizer(self):
        source = inspect.getsource(compatibility_module)
        self.assertIn("normalize_hardware_decision_semantics(", source)

    def test_rule_is_compatible_with_minifix_evidence(self):
        result = compatibility_module.apply_compatibility_decision_rule(
            self._decision_with_evidence(
                "MinifixValidationReport:VALID-1",
                ("blocking clearance warning", "invalid spacing"),
            )
        )

        self.assertEqual(result.compatibility_status, HardwareCompatibilityStatus.BLOCKED)
        self.assertIn("blocking clearance warning", result.quality_impact_note)

    def test_rule_is_compatible_with_confirmat_style_evidence(self):
        result = compatibility_module.apply_compatibility_decision_rule(
            self._decision_with_evidence(
                "ConfirmatValidationReport:VALID-2",
                ("warning: review edge distance",),
            )
        )

        self.assertEqual(result.compatibility_status, HardwareCompatibilityStatus.NEEDS_REVIEW)
        self.assertIn("ConfirmatValidationReport:VALID-2", result.manufacturing_impact_note)

    def test_rule_is_compatible_with_future_hardware_evidence(self):
        result = compatibility_module.apply_compatibility_decision_rule(
            self._decision_with_evidence(
                "FutureFastenerValidationReport:VALID-9",
                ("warning: review future fastener fit",),
            )
        )

        self.assertEqual(result.compatibility_status, HardwareCompatibilityStatus.NEEDS_REVIEW)
        self.assertIn("FutureFastenerValidationReport:VALID-9", result.manufacturing_impact_note)

    def test_source_name_does_not_change_behavior_when_signals_are_identical(self):
        minifix_result = compatibility_module.apply_compatibility_decision_rule(
            self._decision_with_evidence(
                "MinifixValidationReport:VALID-1",
                ("warning: review connector fit",),
            )
        )
        confirmat_result = compatibility_module.apply_compatibility_decision_rule(
            self._decision_with_evidence(
                "ConfirmatValidationReport:VALID-2",
                ("warning: review connector fit",),
            )
        )

        self.assertEqual(
            minifix_result.compatibility_status,
            confirmat_result.compatibility_status,
        )
        self.assertEqual(
            minifix_result.quality_impact_note,
            confirmat_result.quality_impact_note,
        )

    def test_rule_has_no_manufacturing_rule_engine_adapter_or_hardware_specific_branching(self):
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
            "adapter",
            "recommend(",
            "select_hardware",
            "calculate_cost",
            "startswith(\"minifix",
            "startswith(\"confirmat",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
