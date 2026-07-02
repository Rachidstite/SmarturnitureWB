import inspect
import unittest
from dataclasses import fields
from importlib import import_module

import domain.hardware_decision_evidence as evidence_module
from domain.hardware_decision_evidence import HardwareDecisionEvidence
from manufacturing.back_panel_decision_report import BackPanelDecisionReport
from manufacturing.back_panel_validation_report import BackPanelValidationReport
from manufacturing.confirmat_validation_report import ConfirmatValidationReport
from manufacturing.drawer_decision_report import DrawerDecisionReport
from manufacturing.hardware_intelligence_report import HardwareIntelligenceReport
from manufacturing.hardware_placement_report import HardwarePlacementReport
from manufacturing.manufacturing_validation_report import ManufacturingValidationReport
from manufacturing.minifix_validation_report import MinifixValidationReport


NORMALIZER_MODULE_CANDIDATES = (
    "domain.hardware_decision_semantic_normalization",
    "domain.hardware_decision_semantics",
    "domain.hardware_decision_signal_normalization",
)
NORMALIZER_FUNCTION_CANDIDATES = (
    "normalize_hardware_decision_semantics",
    "normalize_hardware_decision_signals",
    "normalize_hardware_decision_evidence",
)


def _field_names(report_cls) -> set[str]:
    return set(getattr(report_cls, "__dataclass_fields__", {}).keys())


def _load_normalizer_target():
    for module_name in NORMALIZER_MODULE_CANDIDATES:
        try:
            module = import_module(module_name)
        except ModuleNotFoundError:
            continue
        for function_name in NORMALIZER_FUNCTION_CANDIDATES:
            target = getattr(module, function_name, None)
            if callable(target):
                return module, target

    raise AssertionError(
        "Missing contract target: expected a semantic normalization entrypoint such as "
        "'domain.hardware_decision_semantic_normalization.normalize_hardware_decision_semantics' "
        "or an equivalent generic semantic-normalization callable."
    )


def _read(output, key):
    if isinstance(output, dict):
        return output.get(key)
    return getattr(output, key)


class TestHardwareDecisionSemanticNormalizationContract(unittest.TestCase):
    def test_existing_report_semantic_fields_are_recognized_as_preferred_inputs(self):
        self.assertTrue({"is_valid", "validation_status"}.issubset(_field_names(MinifixValidationReport)))
        self.assertTrue({"is_valid", "validation_status"}.issubset(_field_names(ConfirmatValidationReport)))
        self.assertTrue(
            {"decision_status", "is_blocked", "requires_review"}.issubset(
                _field_names(BackPanelDecisionReport)
            )
        )
        self.assertTrue(
            {"decision_status", "is_blocked", "requires_review"}.issubset(
                _field_names(DrawerDecisionReport)
            )
        )
        self.assertTrue({"requires_review"}.issubset(_field_names(HardwareIntelligenceReport)))
        self.assertTrue(
            {"hardware_risk", "placement_quality"}.issubset(
                _field_names(HardwarePlacementReport)
            )
        )
        self.assertTrue(
            {"blocking_issue_count", "warning_count"}.issubset(
                _field_names(ManufacturingValidationReport)
            )
        )
        self.assertTrue(
            {"is_valid", "validation_status", "center_support_required"}.issubset(
                _field_names(BackPanelValidationReport)
            )
        )

    def test_hardware_decision_evidence_remains_unchanged_for_v1(self):
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

    def test_future_semantic_normalizer_entrypoint_exists(self):
        _, target = _load_normalizer_target()
        self.assertEqual(list(inspect.signature(target).parameters), ["signals"])

    def test_minifix_semantic_fields_are_preferred_over_warning_text(self):
        _, target = _load_normalizer_target()
        normalized = target(
            {
                "source_type": "MinifixValidationReport",
                "source_ref": "MinifixValidationReport:VALID-1",
                "semantic_fields": {
                    "is_valid": False,
                    "validation_status": "INVALID",
                    "spacing_risk": "HIGH",
                },
                "messages": ("warning text that should not override invalid status",),
            }
        )

        self.assertEqual(_read(normalized, "status"), "INVALID")
        self.assertFalse(_read(normalized, "used_text_fallback"))

    def test_confirmat_semantic_fields_are_preferred_over_warning_text(self):
        _, target = _load_normalizer_target()
        normalized = target(
            {
                "source_type": "ConfirmatValidationReport",
                "source_ref": "ConfirmatValidationReport:VALID-1",
                "semantic_fields": {
                    "is_valid": False,
                    "validation_status": "INVALID",
                    "assembly_risk": "MEDIUM",
                },
                "messages": ("warning text only as secondary evidence",),
            }
        )

        self.assertEqual(_read(normalized, "status"), "INVALID")
        self.assertFalse(_read(normalized, "used_text_fallback"))

    def test_back_panel_blocking_and_review_fields_are_preferred_over_warning_text(self):
        _, target = _load_normalizer_target()
        blocked = target(
            {
                "source_type": "BackPanelDecisionReport",
                "source_ref": "BackPanelDecisionReport:BACK-1",
                "semantic_fields": {
                    "decision_status": "BLOCKED",
                    "is_blocked": True,
                    "requires_review": False,
                },
                "messages": ("warning text",),
            }
        )
        review = target(
            {
                "source_type": "BackPanelDecisionReport",
                "source_ref": "BackPanelDecisionReport:BACK-2",
                "semantic_fields": {
                    "decision_status": "REVIEW_REQUIRED",
                    "is_blocked": False,
                    "requires_review": True,
                },
                "messages": ("warning text",),
            }
        )

        self.assertTrue(_read(blocked, "is_blocked"))
        self.assertEqual(_read(review, "status"), "NEEDS_REVIEW")
        self.assertFalse(_read(blocked, "used_text_fallback"))
        self.assertFalse(_read(review, "used_text_fallback"))

    def test_drawer_blocking_and_review_fields_are_preferred_over_warning_text(self):
        _, target = _load_normalizer_target()
        normalized = target(
            {
                "source_type": "DrawerDecisionReport",
                "source_ref": "DrawerDecisionReport:DRAWER-1",
                "semantic_fields": {
                    "decision_status": "BLOCKED",
                    "is_blocked": True,
                    "requires_review": False,
                },
                "messages": ("warning text",),
            }
        )

        self.assertTrue(_read(normalized, "is_blocked"))
        self.assertEqual(_read(normalized, "status"), "BLOCKED")
        self.assertFalse(_read(normalized, "used_text_fallback"))

    def test_hardware_intelligence_and_placement_semantics_are_preferred_over_warning_text(self):
        _, target = _load_normalizer_target()
        intelligence = target(
            {
                "source_type": "HardwareIntelligenceReport",
                "source_ref": "HardwareIntelligenceReport:INTEL-1",
                "semantic_fields": {"requires_review": True},
                "messages": ("warning text",),
            }
        )
        placement = target(
            {
                "source_type": "HardwarePlacementReport",
                "source_ref": "HardwarePlacementReport:PLACE-1",
                "semantic_fields": {
                    "hardware_risk": "HIGH",
                    "placement_quality": "POOR",
                },
                "messages": ("warning text",),
            }
        )

        self.assertEqual(_read(intelligence, "status"), "NEEDS_REVIEW")
        self.assertEqual(_read(placement, "severity"), "RISK")
        self.assertFalse(_read(intelligence, "used_text_fallback"))
        self.assertFalse(_read(placement, "used_text_fallback"))

    def test_manufacturing_validation_counts_are_preferred_over_warning_text(self):
        _, target = _load_normalizer_target()
        blocked = target(
            {
                "source_type": "ManufacturingValidationReport",
                "source_ref": "ManufacturingValidationReport:MANUF-1",
                "semantic_fields": {
                    "blocking_issue_count": 2,
                    "warning_count": 0,
                    "ready_for_manufacturing": False,
                },
                "messages": ("warning text",),
            }
        )
        review = target(
            {
                "source_type": "ManufacturingValidationReport",
                "source_ref": "ManufacturingValidationReport:MANUF-2",
                "semantic_fields": {
                    "blocking_issue_count": 0,
                    "warning_count": 2,
                    "ready_for_manufacturing": False,
                },
                "messages": ("warning text",),
            }
        )

        self.assertEqual(_read(blocked, "status"), "BLOCKED")
        self.assertEqual(_read(review, "status"), "WARNING")
        self.assertFalse(_read(blocked, "used_text_fallback"))
        self.assertFalse(_read(review, "used_text_fallback"))

    def test_text_parsing_is_allowed_only_as_fallback_when_no_semantic_fields_exist(self):
        _, target = _load_normalizer_target()
        normalized = target(
            {
                "source_type": "UnknownReport",
                "source_ref": "UnknownReport:FALLBACK-1",
                "semantic_fields": {},
                "messages": ("warning: fallback parsing allowed",),
            }
        )

        self.assertTrue(_read(normalized, "used_text_fallback"))
        self.assertIn(_read(normalized, "status"), {"WARNING", "NEEDS_REVIEW", "RISK"})

    def test_contract_requires_normalized_semantic_signals_before_raw_messages(self):
        _, target = _load_normalizer_target()
        normalized = target(
            {
                "source_type": "MinifixValidationReport",
                "source_ref": "MinifixValidationReport:VALID-2",
                "semantic_fields": {"validation_status": "VALID", "is_valid": True},
                "messages": ("blocked text that should not win over semantic pass",),
            }
        )

        self.assertIn(_read(normalized, "status"), {"VALID", "PASS"})
        self.assertFalse(_read(normalized, "used_text_fallback"))

    def test_no_adapter_or_runtime_geometry_cost_ui_dependencies_are_required(self):
        source = inspect.getsource(evidence_module).lower()
        for token in (
            "adapter",
            "geometryengine",
            "scenegraph",
            "runtime",
            "freecad",
            "applicationservice",
            "cost_intelligence",
            "import ui",
            "from ui",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
