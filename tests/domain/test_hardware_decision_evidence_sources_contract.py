import inspect
import unittest
from dataclasses import fields
from importlib import import_module

import domain.hardware_decision_evidence as evidence_module
from domain.hardware_decision_evidence import HardwareDecisionEvidence


APPROVED_EVIDENCE_SOURCES = (
    ("manufacturing.hardware_placement_report", "HardwarePlacementReport"),
    ("manufacturing.minifix_validation_report", "MinifixValidationReport"),
    ("manufacturing.confirmat_validation_report", "ConfirmatValidationReport"),
    ("manufacturing.back_panel_decision_report", "BackPanelDecisionReport"),
    ("manufacturing.drawer_decision_report", "DrawerDecisionReport"),
    ("manufacturing.hardware_intelligence_report", "HardwareIntelligenceReport"),
    ("manufacturing.hardware_usage_report", "HardwareUsageReport"),
    ("manufacturing.factory_operational_report", "FactoryOperationalReport"),
    ("manufacturing.production_schedule_report", "ProductionScheduleReport"),
    ("manufacturing.labor_cost_report", "LaborCostReport"),
)


def _import_optional_report(module_name: str, class_name: str):
    try:
        module = import_module(module_name)
    except ModuleNotFoundError as exc:
        raise unittest.SkipTest(
            f"{class_name} skipped: module '{module_name}' is not present."
        ) from exc

    report_class = getattr(module, class_name, None)
    if report_class is None:
        raise unittest.SkipTest(
            f"{class_name} skipped: class '{class_name}' is not present in '{module_name}'."
        )
    return module, report_class


def _reference_for(report_class_name: str, *, report_id=None, fallback_label="DEFAULT") -> str:
    suffix = str(report_id or fallback_label or "DEFAULT")
    return f"{report_class_name}:{suffix}"


class TestHardwareDecisionEvidenceSourcesContract(unittest.TestCase):
    def test_approved_evidence_source_report_classes_exist_or_are_explicitly_skipped(self):
        found = []
        skipped = []

        for module_name, class_name in APPROVED_EVIDENCE_SOURCES:
            try:
                _, report_class = _import_optional_report(module_name, class_name)
            except unittest.SkipTest as exc:
                skipped.append(str(exc))
                continue
            found.append(report_class.__name__)

        self.assertGreater(len(found) + len(skipped), 0)
        self.assertEqual(len(found), len(APPROVED_EVIDENCE_SOURCES))

    def test_hardware_decision_evidence_stores_only_reference_and_note_fields(self):
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

    def test_report_references_are_strings_only(self):
        evidence = HardwareDecisionEvidence(
            evidence_id="EVID-1",
            placement_report_refs=("HardwarePlacementReport:PLACEMENT-1",),
            validation_report_refs=("MinifixValidationReport:VALIDATION-1",),
            compatibility_report_refs=("HardwareIntelligenceReport:COMPAT-1",),
            manufacturing_report_refs=("FactoryOperationalReport:OPS-1",),
            cost_report_refs=("LaborCostReport:COST-1",),
            warnings=("warning",),
            blocking_constraints=("constraint",),
            source_rules=("rule_name",),
            source_components=("component_name",),
            evidence_notes=("note",),
        )

        for field_name in (
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
        ):
            values = getattr(evidence, field_name)
            self.assertTrue(all(isinstance(item, str) for item in values))

    def test_reference_strings_include_source_type_and_identifier_or_fallback_label(self):
        explicit = _reference_for("HardwarePlacementReport", report_id="PLACEMENT-1")
        fallback = _reference_for(
            "ProductionScheduleReport",
            fallback_label="schedule_risk_level",
        )

        self.assertEqual(explicit, "HardwarePlacementReport:PLACEMENT-1")
        self.assertEqual(fallback, "ProductionScheduleReport:schedule_risk_level")
        self.assertIn(":", explicit)
        self.assertIn(":", fallback)

    def test_report_id_is_not_required_for_reference_generation(self):
        reference = _reference_for(
            "DrawerDecisionReport",
            report_id=None,
            fallback_label="warning_reason",
        )

        self.assertEqual(reference, "DrawerDecisionReport:warning_reason")

    def test_source_rules_and_components_may_be_supplied_externally_later(self):
        evidence = HardwareDecisionEvidence(
            source_rules=(),
            source_components=(),
        )

        self.assertEqual(evidence.source_rules, ())
        self.assertEqual(evidence.source_components, ())

    def test_no_object_level_coupling_to_manufacturing_reports_is_required(self):
        source = inspect.getsource(evidence_module)

        for module_name, _ in APPROVED_EVIDENCE_SOURCES:
            self.assertNotIn(module_name, source)

    def test_no_evidence_adapter_is_required_by_contract(self):
        source = inspect.getsource(evidence_module).lower()

        self.assertNotIn("adapter", source)
        self.assertNotIn("adapt(", source)

    def test_no_rules_recommendation_or_scoring_logic_is_present(self):
        source = inspect.getsource(evidence_module).lower()

        for token in (
            "rule_engine",
            "execute_rule",
            "evaluate_rule",
            "recommendation_engine",
            "recommend(",
            "score(",
            "scoring",
            "workflow",
            "pipeline",
        ):
            self.assertNotIn(token, source)

    def test_no_geometry_scenegraph_runtime_freecad_ui_or_application_dependency(self):
        source = inspect.getsource(evidence_module).lower()

        for token in (
            "geometryengine",
            "scenegraph",
            "runtime",
            "freecad",
            "applicationservice",
            "import ui",
            "from ui",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
