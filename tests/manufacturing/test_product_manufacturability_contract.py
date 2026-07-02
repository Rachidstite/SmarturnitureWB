import importlib
import inspect
import unittest
from dataclasses import dataclass
from types import SimpleNamespace

from manufacturing.manufacturing_decision import ManufacturingDecision
from manufacturing.manufacturing_validation_summary_report import (
    ManufacturingValidationSummaryReport,
)
from manufacturing.project_manufacturing_readiness_report import (
    ProjectManufacturingReadinessReport,
)
from project_engineering.project_engineering_readiness_report import (
    ProjectEngineeringReadinessReport,
)


@dataclass(frozen=True)
class ProductManufacturabilityContractState:
    manufacturable: bool
    manufacturable_with_warnings: bool
    requires_review: bool
    blocked: bool


class TestProductManufacturabilityContract(unittest.TestCase):
    def setUp(self):
        from manufacturing.manufacturing_decision_builder import (
            ManufacturingDecisionBuilder,
        )
        from manufacturing.project_manufacturing_readiness_builder import (
            ProjectManufacturingReadinessBuilder,
        )

        self.manufacturing_decision_builder = ManufacturingDecisionBuilder()
        self.project_readiness_builder = ProjectManufacturingReadinessBuilder()

    def test_existing_components_provide_product_level_evidence(self):
        components = (
            ProjectManufacturingReadinessReport,
            ManufacturingValidationSummaryReport,
            ManufacturingDecision,
        )

        for component in components:
            with self.subTest(component=component.__name__):
                self.assertTrue(inspect.isclass(component))

        from manufacturing.manufacturing_production_package import (
            ProductionEvidenceView,
        )

        self.assertTrue(inspect.isclass(ProductionEvidenceView))

    def test_product_manufacturability_is_expressible_without_new_engine(self):
        module_names = (
            "manufacturing.project_manufacturing_readiness_builder",
            "manufacturing.manufacturing_decision_builder",
            "manufacturing.manufacturing_production_package",
        )

        combined_source = "\n".join(
            inspect.getsource(importlib.import_module(module_name))
            for module_name in module_names
        )

        self.assertNotIn("ManufacturabilityEngine", combined_source)
        self.assertNotIn("ManufacturingEngine", combined_source)
        self.assertNotIn("NewWorkflow", combined_source)
        self.assertNotIn("Adapter", combined_source)

    def test_product_manufacturability_categories_can_be_derived_from_existing_outputs(
        self,
    ):
        clean_decision = self.manufacturing_decision_builder.build(
            engineering_readiness_report=self._engineering_ready(),
            manufacturing_validation_summary_report=self._validation_summary(),
            release_validation={"ready": True, "warnings": []},
            project_manufacturing_readiness_report=self._project_readiness("READY"),
            production_evidence=self._production_evidence(
                has_cutlist_evidence=True,
                has_machining_evidence=True,
                has_edge_evidence=True,
                has_hardware_evidence=True,
            ),
        )
        clean_state = self._state_from_decision(clean_decision)
        self.assertTrue(clean_state.manufacturable)
        self.assertFalse(clean_state.manufacturable_with_warnings)
        self.assertFalse(clean_state.requires_review)
        self.assertFalse(clean_state.blocked)

        warning_decision = self.manufacturing_decision_builder.build(
            engineering_readiness_report=self._engineering_ready(),
            manufacturing_validation_summary_report=self._validation_summary(
                warning_count=1,
                warning_messages=["Review manufacturing warning"],
            ),
            project_manufacturing_readiness_report=self._project_readiness("REVIEW"),
            production_evidence=self._production_evidence(
                has_cutlist_evidence=True,
                has_machining_evidence=False,
                has_edge_evidence=True,
                has_hardware_evidence=False,
            ),
        )
        warning_state = self._state_from_decision(warning_decision)
        self.assertTrue(warning_state.manufacturable)
        self.assertTrue(warning_state.manufacturable_with_warnings)
        self.assertTrue(warning_state.requires_review)
        self.assertFalse(warning_state.blocked)

        blocked_decision = self.manufacturing_decision_builder.build(
            engineering_readiness_report=self._engineering_blocked(),
        )
        blocked_state = self._state_from_decision(blocked_decision)
        self.assertFalse(blocked_state.manufacturable)
        self.assertFalse(blocked_state.manufacturable_with_warnings)
        self.assertFalse(blocked_state.requires_review)
        self.assertTrue(blocked_state.blocked)

    def test_blocking_evidence_prevents_manufacturable_true(self):
        decision = self.manufacturing_decision_builder.build(
            manufacturing_validation_summary_report=self._validation_summary(
                blocking_issue_count=1,
                blocking_messages=["Missing structural support"],
            )
        )

        state = self._state_from_decision(decision)
        self.assertTrue(state.blocked)
        self.assertFalse(state.manufacturable)
        self.assertIn("Missing structural support", decision.blocking_reasons)

    def test_warning_evidence_allows_manufacturable_true_but_requires_review(self):
        decision = self.manufacturing_decision_builder.build(
            manufacturing_validation_summary_report=self._validation_summary(
                warning_count=1,
                warning_messages=["Review hardware warning"],
            )
        )

        state = self._state_from_decision(decision)
        self.assertTrue(state.manufacturable)
        self.assertTrue(state.manufacturable_with_warnings)
        self.assertTrue(state.requires_review)
        self.assertFalse(state.blocked)

    def test_missing_cnc_and_hardware_evidence_is_product_level_manufacturing_risk(self):
        decision = self.manufacturing_decision_builder.build(
            engineering_readiness_report=self._engineering_ready(),
            production_evidence=self._production_evidence(
                has_cutlist_evidence=True,
                has_machining_evidence=False,
                has_edge_evidence=True,
                has_hardware_evidence=False,
            ),
        )

        self.assertEqual(decision.status, "WARNING")
        self.assertIn("Missing machining evidence", decision.warning_reasons)
        self.assertIn("Missing hardware evidence", decision.warning_reasons)
        self.assertFalse(decision.ready_for_production)

    def test_structural_failure_is_product_level_blocking_evidence(self):
        report = self.project_readiness_builder.build(
            cabinet_structural_report=SimpleNamespace(
                structural_risk="HIGH",
                stability_risk="LOW",
            ),
        )

        self.assertEqual(report.readiness_status, "BLOCKED")
        self.assertEqual(report.structural_risk, "HIGH")
        self.assertTrue(report.engineering_review_required)

    def test_release_readiness_is_downstream_of_product_level_evidence(self):
        decision = self.manufacturing_decision_builder.build(
            engineering_readiness_report=self._engineering_ready(),
            project_manufacturing_readiness_report=self._project_readiness(
                "BLOCKED",
                "Project manufacturing review required",
            ),
        )

        self.assertEqual(decision.status, "FAIL")
        self.assertFalse(decision.ready_for_production)
        self.assertIn(
            "Project manufacturing review required",
            decision.blocking_reasons,
        )

    def test_manufacturing_decision_remains_the_production_release_gate(self):
        self.assertTrue(
            hasattr(ManufacturingDecision, "ready_for_production"),
        )

        source = inspect.getsource(
            importlib.import_module("manufacturing.manufacturing_decision_builder")
        )
        self.assertIn("ready_for_production", source)
        self.assertNotIn("ManufacturabilityEngine", source)
        self.assertNotIn("build_product_manufacturability", source)

    def test_terminology_matches_ag_12_contract_language(self):
        summary_fields = set(ManufacturingValidationSummaryReport.__dataclass_fields__)
        self.assertIn("warning_count", summary_fields)
        self.assertIn("blocking_issue_count", summary_fields)
        self.assertIn("warning_messages", summary_fields)
        self.assertIn("blocking_messages", summary_fields)

        readiness_fields = set(
            ProjectManufacturingReadinessReport.__dataclass_fields__
        )
        self.assertIn("readiness_status", readiness_fields)

        decision_fields = set(ManufacturingDecision.__dataclass_fields__)
        self.assertIn("ready_for_production", decision_fields)

    def test_assembly_readiness_must_be_connected_to_product_level_aggregation(self):
        combined_source = self._product_level_aggregation_source()

        self.assertRegex(
            combined_source,
            r"assembly_|installation_risk|assembly_complexity",
        )

    def test_shelf_support_readiness_must_be_connected_to_product_level_aggregation(self):
        combined_source = self._product_level_aggregation_source()

        self.assertRegex(
            combined_source,
            r"shelf_|span_risk|sagging_risk|support_required",
        )

    def test_back_panel_and_drawer_readiness_must_be_connectable_at_product_level(self):
        combined_source = self._product_level_aggregation_source()

        self.assertRegex(
            combined_source,
            r"back_panel|drawer",
        )

    @staticmethod
    def _state_from_decision(
        decision: ManufacturingDecision,
    ) -> ProductManufacturabilityContractState:
        blocked = decision.status == "FAIL"
        manufacturable_with_warnings = decision.status == "WARNING"
        manufacturable = decision.status != "FAIL"
        requires_review = decision.status == "WARNING"
        return ProductManufacturabilityContractState(
            manufacturable=manufacturable,
            manufacturable_with_warnings=manufacturable_with_warnings,
            requires_review=requires_review,
            blocked=blocked,
        )

    @staticmethod
    def _product_level_aggregation_source() -> str:
        module_names = (
            "manufacturing.project_manufacturing_readiness_builder",
            "manufacturing.manufacturing_decision_builder",
            "manufacturing.manufacturing_production_package_builder",
        )
        return "\n".join(
            inspect.getsource(importlib.import_module(module_name))
            for module_name in module_names
        )

    @staticmethod
    def _engineering_ready():
        return ProjectEngineeringReadinessReport(
            project_id="PROJECT-1",
            ready_for_engineering_release=True,
            ready_for_manufacturing_handoff=True,
            blocking_violation_count=0,
            warning_count=0,
            source="engineering-readiness-builder",
        )

    @staticmethod
    def _engineering_blocked():
        return ProjectEngineeringReadinessReport(
            project_id="PROJECT-1",
            ready_for_engineering_release=False,
            ready_for_manufacturing_handoff=False,
            blocking_violation_count=1,
            warning_count=0,
            source="engineering-readiness-builder",
        )

    @staticmethod
    def _validation_summary(
        blocking_issue_count=0,
        blocking_messages=(),
        warning_count=0,
        warning_messages=(),
    ):
        return ManufacturingValidationSummaryReport(
            ready_for_manufacturing=(blocking_issue_count == 0),
            total_rule_count=0,
            passed_rule_count=0,
            failed_rule_count=blocking_issue_count + warning_count,
            warning_count=warning_count,
            blocking_issue_count=blocking_issue_count,
            blocking_messages=list(blocking_messages),
            warning_messages=list(warning_messages),
            source="manufacturing-validation-summary-builder",
        )

    @staticmethod
    def _project_readiness(status, recommendation=""):
        return ProjectManufacturingReadinessReport(
            readiness_status=status,
            structural_risk="HIGH" if status == "BLOCKED" else "LOW",
            engineering_review_required=(status != "READY"),
            manufacturing_recommendation=recommendation,
        )

    @staticmethod
    def _production_evidence(
        *,
        has_cutlist_evidence,
        has_machining_evidence,
        has_edge_evidence,
        has_hardware_evidence,
    ):
        return SimpleNamespace(
            release_warnings=(),
            has_cutlist_evidence=has_cutlist_evidence,
            has_machining_evidence=has_machining_evidence,
            has_edge_evidence=has_edge_evidence,
            has_hardware_evidence=has_hardware_evidence,
        )


if __name__ == "__main__":
    unittest.main()
