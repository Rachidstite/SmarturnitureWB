import inspect
import unittest

import domain.hardware_decision_builder as builder_module
from domain.hardware_decision import HardwareCompatibilityStatus
from domain.hardware_decision_context import HardwareDecisionContext
from domain.hardware_decision_evidence import HardwareDecisionEvidence


class TestHardwareDecisionIntegrationContract(unittest.TestCase):
    def _sample_context(self) -> HardwareDecisionContext:
        return HardwareDecisionContext(
            context_id="CTX-HW-INTEGRATION-001",
            product_family="BASE_CABINET",
            cabinet_type="BASE",
            material_type="MDF",
            panel_thickness_mm=18.0,
            cabinet_width_mm=900.0,
            cabinet_height_mm=720.0,
            cabinet_depth_mm=560.0,
            mounting_type="floor",
            required_load_kg=20.0,
            available_hardware_skus=(
                "MINIFIX_15_V1",
                "CONFIRMAT_50_V1",
                "HINGE_BLUM_110_V1",
            ),
            manufacturing_capabilities=("CNC_DRILLING", "SYSTEM32"),
            customer_constraints=("SOFT_CLOSE_REQUIRED",),
            notes=("integration contract context",),
        )

    def _sample_evidence(self) -> HardwareDecisionEvidence:
        return HardwareDecisionEvidence(
            evidence_id="EVID-HW-INTEGRATION-001",
            placement_report_refs=("HardwarePlacementReport:PLACEMENT-1",),
            validation_report_refs=(
                "MinifixValidationReport:VALIDATION-1",
                "ConfirmatValidationReport:VALIDATION-2",
            ),
            compatibility_report_refs=(
                "BackPanelDecisionReport:BACK-1",
                "DrawerDecisionReport:DRAWER-1",
                "HardwareIntelligenceReport:INTEL-1",
                "HardwareUsageReport:USAGE-1",
            ),
            manufacturing_report_refs=("FactoryOperationalReport:OPS-1",),
            cost_report_refs=("LaborCostReport:COST-1",),
            warnings=("warning-a", "warning-b"),
            blocking_constraints=("constraint-a",),
            source_rules=("existing_hardware_rule",),
            source_components=("existing_hardware_validator",),
            evidence_notes=("reference-only evidence",),
        )

    def test_builder_consumes_context_and_evidence_not_raw_reports(self):
        build_fn = getattr(builder_module, "build_hardware_decision", None)
        self.assertTrue(callable(build_fn))
        self.assertEqual(
            list(inspect.signature(build_fn).parameters),
            ["context", "evidence"],
        )

    def test_existing_report_outputs_are_reused_through_evidence_references(self):
        decision = builder_module.build_hardware_decision(
            self._sample_context(),
            self._sample_evidence(),
        )

        self.assertEqual(
            decision.decision.traceability.evidence_refs,
            (
                "HardwarePlacementReport:PLACEMENT-1",
                "MinifixValidationReport:VALIDATION-1",
                "ConfirmatValidationReport:VALIDATION-2",
                "BackPanelDecisionReport:BACK-1",
                "DrawerDecisionReport:DRAWER-1",
                "HardwareIntelligenceReport:INTEL-1",
                "HardwareUsageReport:USAGE-1",
                "FactoryOperationalReport:OPS-1",
                "LaborCostReport:COST-1",
            ),
        )

    def test_builder_may_update_traceability_and_validation_messages_from_evidence(self):
        decision = builder_module.build_hardware_decision(
            self._sample_context(),
            self._sample_evidence(),
        )

        self.assertEqual(
            decision.decision.traceability.source_rule,
            "existing_hardware_rule",
        )
        self.assertEqual(
            decision.decision.traceability.source_component,
            "existing_hardware_validator",
        )
        self.assertEqual(
            decision.decision.validation_messages,
            (
                "warning-a",
                "warning-b",
                "constraint-a",
                "reference-only evidence",
            ),
        )

    def test_cost_reports_are_reused_through_cost_report_refs_only(self):
        decision = builder_module.build_hardware_decision(
            self._sample_context(),
            self._sample_evidence(),
        )

        self.assertIn(
            "LaborCostReport:COST-1",
            decision.decision.traceability.evidence_refs,
        )
        self.assertEqual(decision.cost_impact_note, "")

    def test_builder_does_not_duplicate_selection_or_compatibility_logic(self):
        decision = builder_module.build_hardware_decision(
            self._sample_context(),
            self._sample_evidence(),
        )

        self.assertEqual(decision.selected_hardware_sku, "")
        self.assertEqual(decision.rejected_hardware_skus, ())
        self.assertEqual(
            decision.compatibility_status,
            HardwareCompatibilityStatus.NEEDS_REVIEW,
        )

    def test_builder_remains_deterministic_and_pure(self):
        context = self._sample_context()
        evidence = self._sample_evidence()

        first = builder_module.build_hardware_decision(context, evidence)
        second = builder_module.build_hardware_decision(context, evidence)

        self.assertEqual(first, second)
        self.assertEqual(context, self._sample_context())
        self.assertEqual(evidence, self._sample_evidence())

    def test_builder_has_no_direct_manufacturing_cost_rules_or_runtime_dependencies(self):
        source = inspect.getsource(builder_module).lower()

        for token in (
            "manufacturing.",
            "cost_intelligence.",
            "rules_engine",
            "hardware_library",
            "geometryengine",
            "scenegraph",
            "applicationservice",
            "freecad",
            "recommendation_engine",
            "recommend(",
            "evaluate_compatibility",
            "calculate_hardware_cost",
            "select_hardware",
            "runtime",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
