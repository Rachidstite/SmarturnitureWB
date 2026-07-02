import inspect
import unittest
from dataclasses import FrozenInstanceError

import domain.quality_decision_rule as quality_module
from domain.hardware_decision import HardwareCompatibilityStatus, HardwareDecision
from domain.operational_decision import (
    OperationalDecision,
    OperationalDecisionTraceability,
)


class TestQualityDecisionRuleContract(unittest.TestCase):
    def _decision_with_evidence(self, evidence_ref: str, messages: tuple[str, ...]) -> HardwareDecision:
        return HardwareDecision(
            decision=OperationalDecision(
                decision_id="QUALITY-001",
                traceability=OperationalDecisionTraceability(
                    source_component="hardware_decision_builder",
                    source_rule="quality_validation_evidence",
                    evidence_refs=(evidence_ref,),
                ),
                validation_messages=messages,
            ),
            quality_impact_note="",
        )

    def test_rule_exposes_pure_function_entrypoint(self):
        rule_fn = getattr(quality_module, "apply_quality_decision_rule", None)
        self.assertTrue(callable(rule_fn))
        self.assertEqual(list(inspect.signature(rule_fn).parameters), ["decision"])

    def test_rule_preserves_immutable_input_and_returns_new_decision(self):
        decision = self._decision_with_evidence(
            "HardwarePlacementReport:QUAL-1",
            ("warning: quality review required",),
        )
        result = quality_module.apply_quality_decision_rule(decision)

        self.assertIsInstance(result, HardwareDecision)
        self.assertIsNot(result, decision)
        self.assertEqual(
            decision,
            self._decision_with_evidence(
                "HardwarePlacementReport:QUAL-1",
                ("warning: quality review required",),
            ),
        )
        with self.assertRaises(FrozenInstanceError):
            decision.quality_impact_note = "mutated"

    def test_rule_uses_semantic_normalizer(self):
        source = inspect.getsource(quality_module)
        self.assertIn("normalize_hardware_decision_semantics(", source)

    def test_quality_risk_evidence_updates_quality_impact_note(self):
        result = quality_module.apply_quality_decision_rule(
            self._decision_with_evidence(
                "HardwarePlacementReport:QUAL-2",
                ("risk: placement quality degraded",),
            )
        )

        self.assertIn("Quality evidence: RISK", result.quality_impact_note)
        self.assertIn("risk: placement quality degraded", result.quality_impact_note)

    def test_blocked_or_invalid_quality_evidence_may_block_compatibility(self):
        blocked = quality_module.apply_quality_decision_rule(
            self._decision_with_evidence(
                "MinifixValidationReport:QUAL-3",
                ("blocking quality failure",),
            )
        )
        invalid = quality_module.apply_quality_decision_rule(
            self._decision_with_evidence(
                "ConfirmatValidationReport:QUAL-4",
                ("invalid surface finish",),
            )
        )

        self.assertEqual(blocked.compatibility_status, HardwareCompatibilityStatus.BLOCKED)
        self.assertEqual(invalid.compatibility_status, HardwareCompatibilityStatus.BLOCKED)

    def test_warning_review_or_risk_quality_evidence_updates_note_without_forcing_block(self):
        for messages in (
            ("warning: review finish tolerance",),
            ("review quality alignment",),
            ("risk in edge finish",),
        ):
            with self.subTest(messages=messages):
                result = quality_module.apply_quality_decision_rule(
                    self._decision_with_evidence(
                        "HardwareIntelligenceReport:QUAL-5",
                        messages,
                    )
                )
                self.assertNotEqual(
                    result.compatibility_status,
                    HardwareCompatibilityStatus.BLOCKED,
                )
                self.assertNotEqual(result.quality_impact_note, "")

    def test_valid_or_pass_evidence_does_not_block(self):
        for messages in (
            (),
            ("valid",),
            ("pass",),
        ):
            with self.subTest(messages=messages):
                result = quality_module.apply_quality_decision_rule(
                    self._decision_with_evidence(
                        "BackPanelValidationReport:QUAL-6",
                        messages,
                    )
                )
                self.assertNotEqual(
                    result.compatibility_status,
                    HardwareCompatibilityStatus.BLOCKED,
                )

    def test_evidence_source_name_does_not_affect_behaviour(self):
        placement = quality_module.apply_quality_decision_rule(
            self._decision_with_evidence(
                "HardwarePlacementReport:QUAL-7",
                ("warning: quality review required",),
            )
        )
        intelligence = quality_module.apply_quality_decision_rule(
            self._decision_with_evidence(
                "HardwareIntelligenceReport:QUAL-7",
                ("warning: quality review required",),
            )
        )

        self.assertEqual(placement.compatibility_status, intelligence.compatibility_status)
        self.assertEqual(placement.quality_impact_note, intelligence.quality_impact_note)

    def test_rule_has_no_manufacturing_imports_or_report_specific_branching(self):
        source = inspect.getsource(quality_module).lower()

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
            "startswith(\"hardwareplacement",
            "startswith(\"hardwareintelligence",
            "select_hardware",
            "calculate_cost",
            "recommend(",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
