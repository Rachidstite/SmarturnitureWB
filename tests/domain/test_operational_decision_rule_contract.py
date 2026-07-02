import inspect
import unittest
from dataclasses import FrozenInstanceError

import domain.operational_decision_rule as operational_module
from domain.hardware_decision import HardwareCompatibilityStatus, HardwareDecision
from domain.operational_decision import (
    OperationalDecision,
    OperationalDecisionTraceability,
)


class TestOperationalDecisionRuleContract(unittest.TestCase):
    def _decision_with_evidence(self, evidence_ref: str, messages: tuple[str, ...]) -> HardwareDecision:
        return HardwareDecision(
            decision=OperationalDecision(
                decision_id="OPERATIONAL-001",
                traceability=OperationalDecisionTraceability(
                    source_component="hardware_decision_builder",
                    source_rule="operational_evidence",
                    evidence_refs=(evidence_ref,),
                ),
                validation_messages=messages,
            ),
            manufacturing_impact_note="",
        )

    def test_rule_exposes_pure_function_entrypoint(self):
        rule_fn = getattr(operational_module, "apply_operational_decision_rule", None)
        self.assertTrue(callable(rule_fn))
        self.assertEqual(list(inspect.signature(rule_fn).parameters), ["decision"])

    def test_rule_preserves_immutable_input_and_returns_new_decision(self):
        decision = self._decision_with_evidence(
            "FactoryOperationalReport:OPS-1",
            ("warning: capacity review required",),
        )
        result = operational_module.apply_operational_decision_rule(decision)

        self.assertIsInstance(result, HardwareDecision)
        self.assertIsNot(result, decision)
        self.assertEqual(
            decision,
            self._decision_with_evidence(
                "FactoryOperationalReport:OPS-1",
                ("warning: capacity review required",),
            ),
        )
        with self.assertRaises(FrozenInstanceError):
            decision.manufacturing_impact_note = "mutated"

    def test_rule_uses_semantic_normalizer(self):
        source = inspect.getsource(operational_module)
        self.assertIn("normalize_hardware_decision_semantics(", source)

    def test_operational_warning_evidence_updates_manufacturing_impact_note(self):
        result = operational_module.apply_operational_decision_rule(
            self._decision_with_evidence(
                "FactoryOperationalReport:OPS-2",
                ("warning: operational capacity review required",),
            )
        )

        self.assertIn("Operational evidence: WARNING", result.manufacturing_impact_note)
        self.assertIn(
            "warning: operational capacity review required",
            result.manufacturing_impact_note,
        )

    def test_blocking_operational_evidence_may_set_compatibility_status_blocked(self):
        result = operational_module.apply_operational_decision_rule(
            self._decision_with_evidence(
                "ProductionScheduleReport:OPS-3",
                ("blocking schedule failure",),
            )
        )

        self.assertEqual(result.compatibility_status, HardwareCompatibilityStatus.BLOCKED)

    def test_valid_or_pass_evidence_does_not_block(self):
        for messages in ((), ("valid",), ("pass",)):
            with self.subTest(messages=messages):
                result = operational_module.apply_operational_decision_rule(
                    self._decision_with_evidence(
                        "ManufacturingValidationReport:OPS-4",
                        messages,
                    )
                )
                self.assertNotEqual(
                    result.compatibility_status,
                    HardwareCompatibilityStatus.BLOCKED,
                )

    def test_source_name_does_not_affect_behaviour(self):
        factory = operational_module.apply_operational_decision_rule(
            self._decision_with_evidence(
                "FactoryOperationalReport:OPS-5",
                ("warning: schedule review required",),
            )
        )
        schedule = operational_module.apply_operational_decision_rule(
            self._decision_with_evidence(
                "ProductionScheduleReport:OPS-5",
                ("warning: schedule review required",),
            )
        )

        self.assertEqual(factory.compatibility_status, schedule.compatibility_status)
        self.assertEqual(factory.manufacturing_impact_note, schedule.manufacturing_impact_note)

    def test_rule_has_no_manufacturing_imports_or_report_specific_branching(self):
        source = inspect.getsource(operational_module).lower()

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
            "startswith(\"factoryoperational",
            "startswith(\"productionschedule",
            "select_hardware",
            "calculate_cost",
            "recommend(",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
