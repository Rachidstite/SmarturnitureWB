import inspect
import unittest
from dataclasses import FrozenInstanceError, fields, is_dataclass

import domain.hardware_decision_evidence as evidence_module
from domain.hardware_decision_evidence import HardwareDecisionEvidence


class TestHardwareDecisionEvidenceContract(unittest.TestCase):
    def _sample_evidence(self) -> HardwareDecisionEvidence:
        return HardwareDecisionEvidence(
            evidence_id="EVID-HW-001",
            placement_report_refs=("hardware_placement_report:REF-1",),
            validation_report_refs=("validation_report:REF-2",),
            compatibility_report_refs=("compatibility_report:REF-3",),
            manufacturing_report_refs=("manufacturing_report:REF-4",),
            cost_report_refs=("cost_report:REF-5",),
            warnings=("clearance review required",),
            blocking_constraints=("wall substrate unknown",),
            source_rules=("hardware_clearance_rule",),
            source_components=("hardware_decision_builder",),
            evidence_notes=("references only",),
        )

    def test_evidence_is_immutable(self):
        evidence = self._sample_evidence()

        self.assertTrue(is_dataclass(HardwareDecisionEvidence))
        with self.assertRaises(FrozenInstanceError):
            evidence.evidence_id = "MUTATED"

    def test_evidence_is_pure_domain_model(self):
        self.assertEqual(
            [field.name for field in fields(HardwareDecisionEvidence)],
            [
                "evidence_id",
                "placement_report_refs",
                "validation_report_refs",
                "compatibility_report_refs",
                "manufacturing_report_refs",
                "cost_report_refs",
                "warnings",
                "blocking_constraints",
                "source_rules",
                "source_components",
                "evidence_notes",
            ],
        )

    def test_evidence_stores_references_only_not_report_objects(self):
        evidence = self._sample_evidence()

        self.assertEqual(evidence.placement_report_refs, ("hardware_placement_report:REF-1",))
        self.assertEqual(evidence.validation_report_refs, ("validation_report:REF-2",))
        self.assertEqual(evidence.compatibility_report_refs, ("compatibility_report:REF-3",))
        self.assertEqual(evidence.manufacturing_report_refs, ("manufacturing_report:REF-4",))
        self.assertEqual(evidence.cost_report_refs, ("cost_report:REF-5",))
        for group in (
            evidence.placement_report_refs,
            evidence.validation_report_refs,
            evidence.compatibility_report_refs,
            evidence.manufacturing_report_refs,
            evidence.cost_report_refs,
        ):
            self.assertTrue(all(isinstance(item, str) for item in group))

    def test_evidence_contains_no_builders_rules_or_recommendation_logic(self):
        source = inspect.getsource(evidence_module).lower()

        for token in (
            "builder",
            "rule_engine",
            "execute_rule",
            "evaluate_rule",
            "recommendation_engine",
            "recommend(",
            "workflow",
            "pipeline",
            "import ai",
            "from ai",
            "import agent",
            "from agent",
        ):
            self.assertNotIn(token, source)

    def test_evidence_has_no_forbidden_runtime_or_pipeline_dependencies(self):
        source = inspect.getsource(evidence_module).lower()

        for token in (
            "geometryengine",
            "scenegraph",
            "manufacturingruntimepipelinebuilder",
            "manufacturingpackagebuilder",
            "costpackagebuilder",
            "runtime",
            "freecad",
            "part",
            "applicationservice",
            "import ui",
            "from ui",
        ):
            self.assertNotIn(token, source)

    def test_evidence_is_independent_from_context_and_decision_models(self):
        source = inspect.getsource(evidence_module)

        self.assertNotIn("from domain.hardware_decision_context import", source)
        self.assertNotIn("from domain.hardware_decision import", source)

    def test_evidence_is_suitable_as_future_builder_or_rule_input(self):
        evidence = self._sample_evidence()

        self.assertEqual(evidence.evidence_id, "EVID-HW-001")
        self.assertEqual(evidence.warnings, ("clearance review required",))
        self.assertEqual(evidence.blocking_constraints, ("wall substrate unknown",))
        self.assertEqual(evidence.source_rules, ("hardware_clearance_rule",))
        self.assertEqual(evidence.source_components, ("hardware_decision_builder",))
        self.assertEqual(evidence.evidence_notes, ("references only",))


if __name__ == "__main__":
    unittest.main()
