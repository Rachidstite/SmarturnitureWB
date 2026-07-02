import inspect
import unittest
from dataclasses import FrozenInstanceError

import domain.hardware_decision_builder as builder_module
from domain.hardware_decision import HardwareDecision
from domain.hardware_decision_context import HardwareDecisionContext
from domain.hardware_decision_evidence import HardwareDecisionEvidence
from domain.operational_decision import OperationalDecisionType


class TestHardwareDecisionBuilderEvidenceContract(unittest.TestCase):
    def _sample_context(self) -> HardwareDecisionContext:
        return HardwareDecisionContext(
            context_id="CTX-HW-EVID-001",
            product_family="WALL_CABINET",
            cabinet_type="WALL",
            material_type="MDF",
            panel_thickness_mm=18.0,
            cabinet_width_mm=800.0,
            cabinet_height_mm=720.0,
            cabinet_depth_mm=350.0,
            mounting_type="wall",
            required_load_kg=35.0,
            available_hardware_skus=("HINGE_BLUM_110_V1", "SCREW_4X40"),
            manufacturing_capabilities=("CNC_DRILLING",),
            customer_constraints=("SOFT_CLOSE_REQUIRED",),
            notes=("Context input",),
        )

    def _sample_evidence(self) -> HardwareDecisionEvidence:
        return HardwareDecisionEvidence(
            evidence_id="EVID-HW-001",
            placement_report_refs=("HardwarePlacementReport:PLACEMENT-1",),
            validation_report_refs=("MinifixValidationReport:VALIDATION-1",),
            compatibility_report_refs=("HardwareIntelligenceReport:COMPAT-1",),
            manufacturing_report_refs=("FactoryOperationalReport:OPS-1",),
            cost_report_refs=("LaborCostReport:COST-1",),
            warnings=("clearance review required",),
            blocking_constraints=("wall substrate unknown",),
            source_rules=("hardware_clearance_rule",),
            source_components=("hardware_decision_builder",),
            evidence_notes=("references only",),
        )

    def test_builder_accepts_context_and_evidence(self):
        build_fn = getattr(builder_module, "build_hardware_decision", None)
        self.assertTrue(callable(build_fn))
        self.assertEqual(list(inspect.signature(build_fn).parameters), ["context", "evidence"])

    def test_builder_is_pure_and_deterministic(self):
        context = self._sample_context()
        evidence = self._sample_evidence()

        first = builder_module.build_hardware_decision(context, evidence)
        second = builder_module.build_hardware_decision(context, evidence)

        self.assertEqual(first, second)

    def test_builder_returns_immutable_hardware_decision(self):
        decision = builder_module.build_hardware_decision(
            self._sample_context(),
            self._sample_evidence(),
        )

        self.assertIsInstance(decision, HardwareDecision)
        with self.assertRaises(FrozenInstanceError):
            decision.selected_hardware_sku = "MUTATED"

    def test_context_and_evidence_remain_unchanged(self):
        context = self._sample_context()
        evidence = self._sample_evidence()
        context_before = context
        evidence_before = evidence

        builder_module.build_hardware_decision(context, evidence)

        self.assertEqual(context, context_before)
        self.assertEqual(evidence, evidence_before)

    def test_report_references_are_copied_exactly(self):
        decision = builder_module.build_hardware_decision(
            self._sample_context(),
            self._sample_evidence(),
        )

        self.assertEqual(
            decision.decision.traceability.evidence_refs,
            (
                "HardwarePlacementReport:PLACEMENT-1",
                "MinifixValidationReport:VALIDATION-1",
                "HardwareIntelligenceReport:COMPAT-1",
                "FactoryOperationalReport:OPS-1",
                "LaborCostReport:COST-1",
            ),
        )

    def test_warnings_blocking_constraints_and_notes_are_copied_exactly(self):
        decision = builder_module.build_hardware_decision(
            self._sample_context(),
            self._sample_evidence(),
        )

        self.assertEqual(
            decision.decision.validation_messages,
            (
                "clearance review required",
                "wall substrate unknown",
                "references only",
            ),
        )

    def test_source_rules_and_components_are_copied_exactly(self):
        decision = builder_module.build_hardware_decision(
            self._sample_context(),
            self._sample_evidence(),
        )

        self.assertEqual(
            decision.decision.traceability.source_rule,
            "hardware_clearance_rule",
        )
        self.assertEqual(
            decision.decision.traceability.source_component,
            "hardware_decision_builder",
        )

    def test_missing_values_remain_unset(self):
        context = self._sample_context()
        evidence = HardwareDecisionEvidence()
        decision = builder_module.build_hardware_decision(context, evidence)

        self.assertEqual(decision.decision.decision_id, context.context_id)
        self.assertEqual(decision.decision.decision_type, OperationalDecisionType.HARDWARE)
        self.assertIsNone(decision.decision.selected_option)
        self.assertEqual(decision.decision.traceability.evidence_refs, ())
        self.assertEqual(decision.decision.traceability.source_rule, "")
        self.assertEqual(decision.decision.traceability.source_component, "")
        self.assertEqual(decision.decision.validation_messages, ())
        self.assertEqual(decision.selected_hardware_sku, "")
        self.assertEqual(decision.rejected_hardware_skus, ())

    def test_builder_has_no_rule_recommendation_ai_runtime_or_pipeline_dependencies(self):
        source = inspect.getsource(builder_module).lower()

        for token in (
            "rule_engine",
            "execute_rule",
            "evaluate_rule",
            "recommendation_engine",
            "recommend(",
            "agent",
            "llm",
            "geometryengine",
            "scenegraph",
            "manufacturingruntimepipelinebuilder",
            "manufacturingpackagebuilder",
            "costpackagebuilder",
            "applicationservice",
            "freecad",
            "runtime",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
