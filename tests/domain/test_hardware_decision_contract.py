import inspect
import unittest
from dataclasses import FrozenInstanceError, fields, is_dataclass

import domain.hardware_decision as hardware_decision_module
from domain.hardware_decision import (
    HardwareCompatibilityStatus,
    HardwareDecision,
    HardwareDecisionCategory,
    HardwareInstallationComplexity,
)
from domain.operational_decision import (
    OperationalDecision,
    OperationalDecisionImpact,
    OperationalDecisionOption,
    OperationalDecisionStatus,
    OperationalDecisionTraceability,
    OperationalDecisionType,
)


class TestHardwareDecisionContract(unittest.TestCase):
    def _sample_operational_decision(self) -> OperationalDecision:
        selected = OperationalDecisionOption(
            option_id="OPT-HW-1",
            label="Preferred hinge family",
            description="Hardware candidate option",
            estimated_cost_impact=4.0,
            estimated_time_impact=1.0,
            estimated_quality_impact=2.0,
            risk_level="LOW",
            is_selected=True,
        )
        return OperationalDecision(
            decision_id="DEC-HW-001",
            decision_type=OperationalDecisionType.HARDWARE,
            status=OperationalDecisionStatus.SELECTED,
            selected_option=selected,
            candidate_options=(selected,),
            reason="Selected during hardware review",
            impact=OperationalDecisionImpact(
                engineering_impact=1.0,
                manufacturing_impact=2.0,
                cost_impact=3.0,
                quality_impact=4.0,
                automation_impact=0.0,
                waste_impact=0.0,
            ),
            traceability=OperationalDecisionTraceability(
                source_component="hardware_decision_builder",
                source_report="hardware_placement_report",
                source_rule="hardware_clearance_rule",
                evidence_refs=("HW-REPORT-1",),
            ),
            validation_messages=("validated",),
        )

    def _sample_hardware_decision(self) -> HardwareDecision:
        return HardwareDecision(
            decision=self._sample_operational_decision(),
            hardware_category=HardwareDecisionCategory.HINGE,
            selected_hardware_sku="HINGE_BLUM_110_V1",
            candidate_hardware_skus=(
                "HINGE_BLUM_110_V1",
                "HINGE_BLUM_95_V1",
            ),
            rejected_hardware_skus=("HINGE_BLUM_95_V1",),
            compatibility_status=HardwareCompatibilityStatus.COMPATIBLE,
            installation_complexity=HardwareInstallationComplexity.LOW,
            manufacturing_impact_note="No machining escalation expected",
            cost_impact_note="Preferred SKU stays within cost target",
            quality_impact_note="Preferred SKU improves closing consistency",
            replacement_allowed=True,
            replacement_reason="Equivalent hinge family allowed by policy",
        )

    def test_hardware_decision_is_immutable(self):
        decision = self._sample_hardware_decision()

        self.assertTrue(is_dataclass(HardwareDecision))
        with self.assertRaises(FrozenInstanceError):
            decision.selected_hardware_sku = "MUTATED"

    def test_hardware_decision_reuses_operational_decision(self):
        decision = self._sample_hardware_decision()

        self.assertIsInstance(decision.decision, OperationalDecision)

    def test_hardware_decision_does_not_duplicate_operational_decision_fields(self):
        field_names = {field.name for field in fields(HardwareDecision)}
        for forbidden in (
            "decision_id",
            "decision_type",
            "status",
            "selected_option",
            "candidate_options",
            "reason",
            "impact",
            "traceability",
            "validation_messages",
        ):
            self.assertNotIn(forbidden, field_names)
        self.assertIn("decision", field_names)

    def test_hardware_categories_cover_factory_hardware_domains(self):
        self.assertEqual(
            {item.value for item in HardwareDecisionCategory},
            {
                "JOINERY",
                "HINGE",
                "DRAWER_SLIDE",
                "SHELF_SUPPORT",
                "BACK_PANEL_FIXING",
                "HANDLE",
                "WALL_MOUNT",
                "LEG",
                "FASTENER",
            },
        )

    def test_hardware_decision_can_represent_selected_candidate_and_rejected_skus(self):
        decision = self._sample_hardware_decision()

        self.assertEqual(decision.selected_hardware_sku, "HINGE_BLUM_110_V1")
        self.assertEqual(
            decision.candidate_hardware_skus,
            ("HINGE_BLUM_110_V1", "HINGE_BLUM_95_V1"),
        )
        self.assertEqual(decision.rejected_hardware_skus, ("HINGE_BLUM_95_V1",))

    def test_hardware_decision_can_represent_compatibility_status(self):
        decision = self._sample_hardware_decision()

        self.assertEqual(
            {item.value for item in HardwareCompatibilityStatus},
            {"COMPATIBLE", "INCOMPATIBLE", "NEEDS_REVIEW", "BLOCKED"},
        )
        self.assertEqual(
            decision.compatibility_status,
            HardwareCompatibilityStatus.COMPATIBLE,
        )

    def test_hardware_decision_can_represent_installation_complexity(self):
        decision = self._sample_hardware_decision()

        self.assertEqual(
            {item.value for item in HardwareInstallationComplexity},
            {"LOW", "MEDIUM", "HIGH", "CNC_REQUIRED", "MANUAL_ALLOWED"},
        )
        self.assertEqual(
            decision.installation_complexity,
            HardwareInstallationComplexity.LOW,
        )

    def test_hardware_decision_can_represent_manufacturing_cost_and_quality_notes(self):
        decision = self._sample_hardware_decision()

        self.assertEqual(
            decision.manufacturing_impact_note,
            "No machining escalation expected",
        )
        self.assertEqual(
            decision.cost_impact_note,
            "Preferred SKU stays within cost target",
        )
        self.assertEqual(
            decision.quality_impact_note,
            "Preferred SKU improves closing consistency",
        )

    def test_hardware_decision_can_represent_replacement_permission_and_reason(self):
        decision = self._sample_hardware_decision()

        self.assertTrue(decision.replacement_allowed)
        self.assertEqual(
            decision.replacement_reason,
            "Equivalent hinge family allowed by policy",
        )

    def test_hardware_decision_has_no_forbidden_runtime_or_pipeline_imports(self):
        source = inspect.getsource(hardware_decision_module).lower()

        for token in (
            "geometryengine",
            "scenegraph",
            "manufacturingruntimepipelinebuilder",
            "manufacturingpackagebuilder",
            "costpackagebuilder",
            "applicationservice",
            "freecad",
            "part",
            "import ui",
            "from ui",
        ):
            self.assertNotIn(token, source)

    def test_hardware_decision_contains_no_rule_execution(self):
        source = inspect.getsource(hardware_decision_module).lower()

        for token in (
            "rule_engine",
            "execute_rule",
            "evaluate_rule",
            "apply_rule",
        ):
            self.assertNotIn(token, source)

    def test_hardware_decision_contains_no_recommendation_or_ai_behavior(self):
        source = inspect.getsource(hardware_decision_module).lower()

        for token in (
            "recommendation_engine",
            "recommend(",
            "agent",
            "llm",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
