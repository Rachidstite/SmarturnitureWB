import inspect
import unittest
from dataclasses import FrozenInstanceError, fields, is_dataclass

import domain.operational_decision as decision_module
from domain.operational_decision import (
    OperationalDecision,
    OperationalDecisionImpact,
    OperationalDecisionOption,
    OperationalDecisionStatus,
    OperationalDecisionTraceability,
    OperationalDecisionType,
)


class TestOperationalDecisionContract(unittest.TestCase):
    def _sample_option(self, option_id: str, *, is_selected: bool) -> OperationalDecisionOption:
        return OperationalDecisionOption(
            option_id=option_id,
            label=f"Option {option_id}",
            description="Factory operational candidate",
            estimated_cost_impact=12.5,
            estimated_time_impact=3.0,
            estimated_quality_impact=1.0,
            risk_level="MEDIUM",
            is_selected=is_selected,
        )

    def _sample_decision(self) -> OperationalDecision:
        selected = self._sample_option("OPT-1", is_selected=True)
        rejected = self._sample_option("OPT-2", is_selected=False)
        return OperationalDecision(
            decision_id="DEC-001",
            decision_type=OperationalDecisionType.HARDWARE,
            status=OperationalDecisionStatus.SELECTED,
            selected_option=selected,
            candidate_options=(selected, rejected),
            reason="Selected after engineering review",
            impact=OperationalDecisionImpact(
                engineering_impact=1.0,
                manufacturing_impact=2.0,
                cost_impact=3.0,
                quality_impact=4.0,
                automation_impact=5.0,
                waste_impact=6.0,
            ),
            traceability=OperationalDecisionTraceability(
                source_component="hardware_family_builder",
                source_report="hardware_risk_report",
                source_rule="hinge_clearance_rule",
                evidence_refs=("REPORT-1", "RULE-2"),
            ),
            validation_messages=("reviewed",),
        )

    def test_decision_model_is_immutable(self):
        decision = self._sample_decision()

        self.assertTrue(is_dataclass(OperationalDecision))
        self.assertTrue(is_dataclass(OperationalDecisionOption))
        self.assertTrue(is_dataclass(OperationalDecisionImpact))
        self.assertTrue(is_dataclass(OperationalDecisionTraceability))

        with self.assertRaises(FrozenInstanceError):
            decision.reason = "mutated"

    def test_decision_type_vocabulary_covers_factory_decision_domains(self):
        self.assertEqual(
            {item.value for item in OperationalDecisionType},
            {
                "HARDWARE",
                "ASSEMBLY",
                "MACHINING",
                "MATERIAL",
                "COST",
                "OPTIMIZATION",
                "PACKAGING",
                "SHIPPING",
                "QUALITY",
            },
        )

    def test_decision_status_vocabulary_supports_lifecycle_states(self):
        self.assertEqual(
            {item.value for item in OperationalDecisionStatus},
            {
                "PROPOSED",
                "SELECTED",
                "REJECTED",
                "NEEDS_REVIEW",
                "BLOCKED",
            },
        )

    def test_decision_can_represent_selected_and_rejected_options(self):
        decision = self._sample_decision()

        self.assertEqual(decision.selected_option.option_id, "OPT-1")
        self.assertEqual(len(decision.candidate_options), 2)
        self.assertTrue(decision.candidate_options[0].is_selected)
        self.assertFalse(decision.candidate_options[1].is_selected)
        self.assertEqual(decision.status, OperationalDecisionStatus.SELECTED)

    def test_decision_can_represent_business_impact_dimensions(self):
        impact = self._sample_decision().impact

        self.assertEqual(
            [field.name for field in fields(OperationalDecisionImpact)],
            [
                "engineering_impact",
                "manufacturing_impact",
                "cost_impact",
                "quality_impact",
                "automation_impact",
                "waste_impact",
            ],
        )
        self.assertEqual(impact.engineering_impact, 1.0)
        self.assertEqual(impact.manufacturing_impact, 2.0)
        self.assertEqual(impact.cost_impact, 3.0)
        self.assertEqual(impact.quality_impact, 4.0)
        self.assertEqual(impact.automation_impact, 5.0)
        self.assertEqual(impact.waste_impact, 6.0)

    def test_decision_can_store_traceability_back_to_reports_and_rules(self):
        traceability = self._sample_decision().traceability

        self.assertEqual(
            [field.name for field in fields(OperationalDecisionTraceability)],
            [
                "source_component",
                "source_report",
                "source_rule",
                "evidence_refs",
            ],
        )
        self.assertEqual(traceability.source_component, "hardware_family_builder")
        self.assertEqual(traceability.source_report, "hardware_risk_report")
        self.assertEqual(traceability.source_rule, "hinge_clearance_rule")
        self.assertEqual(traceability.evidence_refs, ("REPORT-1", "RULE-2"))

    def test_decision_contains_required_fields(self):
        self.assertEqual(
            [field.name for field in fields(OperationalDecision)],
            [
                "decision_id",
                "decision_type",
                "status",
                "selected_option",
                "candidate_options",
                "reason",
                "impact",
                "traceability",
                "validation_messages",
            ],
        )

    def test_decision_model_has_no_forbidden_runtime_or_pipeline_imports(self):
        source = inspect.getsource(decision_module)
        lowered = source.lower()

        for token in (
            "geometryengine",
            "scenegraph",
            "manufacturingruntimepipelinebuilder",
            "manufacturingpackagebuilder",
            "costpackagebuilder",
            "commercialpackagebuilder",
            "applicationservice",
            "freecad",
            "part",
            "ui",
        ):
            self.assertNotIn(token, lowered)

    def test_decision_model_contains_no_rule_execution(self):
        source = inspect.getsource(decision_module).lower()

        for token in (
            "rule_engine",
            "execute_rule",
            "evaluate_rule",
            "apply_rule",
        ):
            self.assertNotIn(token, source)

    def test_decision_model_contains_no_recommendation_or_ai_behavior(self):
        source = inspect.getsource(decision_module).lower()

        for token in (
            "recommendation_engine",
            "recommend(",
            "agent",
            "ai",
            "llm",
        ):
            self.assertNotIn(token, source)

    def test_decision_model_is_suitable_for_hardware_assembly_machining_and_material(self):
        decision_types = {
            OperationalDecisionType.HARDWARE,
            OperationalDecisionType.ASSEMBLY,
            OperationalDecisionType.MACHINING,
            OperationalDecisionType.MATERIAL,
        }

        for decision_type in decision_types:
            decision = OperationalDecision(
                decision_id=f"DEC-{decision_type.value}",
                decision_type=decision_type,
                status=OperationalDecisionStatus.PROPOSED,
                selected_option=None,
                candidate_options=(self._sample_option("OPT-1", is_selected=False),),
                reason="Vocabulary-only contract",
                impact=OperationalDecisionImpact(),
                traceability=OperationalDecisionTraceability(),
                validation_messages=(),
            )
            self.assertEqual(decision.decision_type, decision_type)


if __name__ == "__main__":
    unittest.main()
