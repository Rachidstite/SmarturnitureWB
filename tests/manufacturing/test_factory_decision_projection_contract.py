import inspect
import unittest
from dataclasses import fields, is_dataclass

import manufacturing.factory_decision_projection as projection_module
from commercial_outputs.commercial_package_report import CommercialPackageReport
from cost_intelligence.quotation_document import QuotationDocumentV1
from manufacturing.factory_decision_projection import (
    DecisionProjectionSection,
    FactoryDecisionProjection,
)
from manufacturing.factory_release_package import FactoryReleasePackage
from manufacturing.manufacturing_decision import ManufacturingDecision
from manufacturing.manufacturing_production_package import (
    ManufacturingProductionPackage,
)
from manufacturing.manufacturing_validation_summary_report import (
    ManufacturingValidationSummaryReport,
)


class TestFactoryDecisionProjectionContract(unittest.TestCase):
    def test_section_contract_is_dataclass(self):
        self.assertTrue(is_dataclass(DecisionProjectionSection))
        self.assertEqual(
            [field.name for field in fields(DecisionProjectionSection)],
            [
                "source_object",
                "source_field",
                "source_value",
                "meaning",
                "user_decision_supported",
            ],
        )

    def test_projection_contract_is_dataclass(self):
        self.assertTrue(is_dataclass(FactoryDecisionProjection))
        self.assertEqual(
            [field.name for field in fields(FactoryDecisionProjection)],
            [
                "readiness_summary",
                "blocking_issues",
                "warning_summary",
                "manufacturing_output_status",
                "assembly_status",
                "commercial_status",
                "visualization_status",
                "recommended_next_actions",
                "release_decision",
            ],
        )

    def test_projection_defaults_are_safe(self):
        projection = FactoryDecisionProjection()

        self.assertEqual(projection.blocking_issues, ())
        self.assertEqual(projection.manufacturing_output_status, ())
        self.assertEqual(projection.recommended_next_actions, ())
        self.assertIsNone(projection.visualization_status)
        self.assertIsInstance(projection.readiness_summary, DecisionProjectionSection)
        self.assertIsInstance(projection.warning_summary, DecisionProjectionSection)
        self.assertIsInstance(projection.assembly_status, DecisionProjectionSection)
        self.assertIsInstance(projection.commercial_status, DecisionProjectionSection)
        self.assertIsInstance(projection.release_decision, DecisionProjectionSection)

    def test_projection_is_frozen(self):
        projection = FactoryDecisionProjection()

        with self.assertRaises((AttributeError, TypeError)):
            projection.readiness_summary = DecisionProjectionSection()

        with self.assertRaises((AttributeError, TypeError)):
            projection.readiness_summary.source_field = "status"

    def test_projection_preserves_source_values(self):
        manufacturing_decision = ManufacturingDecision(
            status="WARNING",
            ready_for_production=False,
            blocking_reasons=("Missing material assignment",),
            warning_reasons=("Review edge data",),
            recommended_action="Review production evidence",
            legacy_readiness_status="REVIEW",
            source="manufacturing-decision",
        )
        validation_summary = ManufacturingValidationSummaryReport(
            ready_for_manufacturing=False,
            total_rule_count=2,
            passed_rule_count=1,
            failed_rule_count=1,
            warning_count=1,
            blocking_issue_count=1,
            blocking_messages=["Missing material assignment"],
            warning_messages=["Review edge data"],
            source="validation-summary",
        )
        production_package = ManufacturingProductionPackage(
            cutlist_report=object(),
            edge_report=object(),
            machining_report=object(),
            hardware_report=object(),
            assembly_report=object(),
            cnc_report=object(),
            warnings=["Review edge data"],
            release_ready=False,
        )
        release_package = FactoryReleasePackage(
            manufacturing_decision=manufacturing_decision,
            cut_list=production_package.cutlist_report,
            hardware_bom=production_package.hardware_report,
            cnc_package=production_package.cnc_report,
            assembly_package=production_package.assembly_report,
            warnings=list(production_package.warnings),
            metadata={"project": "base-cabinet"},
        )
        commercial_report = CommercialPackageReport(
            cost_report=object(),
            estimated_price=2500.0,
            margin_amount=300.0,
            margin_percent=12.0,
            warnings=["No commercial pricing policy configured."],
            source="CommercialPackageBuilder",
        )
        quotation_document = QuotationDocumentV1(
            quotation_number="Q-2026-001",
            issue_date="2026-07-01",
            valid_until="2026-08-01",
            seller_name="Smart Furniture",
            customer_name="Example Customer",
            project_description="Base cabinet",
            total_amount=2500.0,
            currency="MAD",
            notes="",
            payment_terms="30% deposit",
        )

        projection = FactoryDecisionProjection(
            readiness_summary=DecisionProjectionSection(
                source_object=manufacturing_decision,
                source_field="status",
                source_value=manufacturing_decision.status,
                meaning="Compact readiness state.",
                user_decision_supported="Approve / hold / reject",
            ),
            blocking_issues=(
                DecisionProjectionSection(
                    source_object=manufacturing_decision,
                    source_field="blocking_reasons",
                    source_value=manufacturing_decision.blocking_reasons,
                    meaning="Reasons that must be fixed first.",
                    user_decision_supported="Fix-first decision",
                ),
                DecisionProjectionSection(
                    source_object=validation_summary,
                    source_field="blocking_messages",
                    source_value=validation_summary.blocking_messages,
                    meaning="Validation blockers reported upstream.",
                    user_decision_supported="Fix-first decision",
                ),
            ),
            warning_summary=DecisionProjectionSection(
                source_object=manufacturing_decision,
                source_field="warning_reasons",
                source_value=manufacturing_decision.warning_reasons,
                meaning="Non-blocking concerns.",
                user_decision_supported="Review / accept with warnings",
            ),
            manufacturing_output_status=(
                DecisionProjectionSection(
                    source_object=release_package,
                    source_field="cut_list",
                    source_value=release_package.cut_list,
                    meaning="Panel cutting evidence is present.",
                    user_decision_supported="Output completeness",
                ),
                DecisionProjectionSection(
                    source_object=release_package,
                    source_field="hardware_bom",
                    source_value=release_package.hardware_bom,
                    meaning="Hardware evidence is present.",
                    user_decision_supported="Output completeness",
                ),
                DecisionProjectionSection(
                    source_object=release_package,
                    source_field="cnc_package",
                    source_value=release_package.cnc_package,
                    meaning="CNC evidence is present.",
                    user_decision_supported="Output completeness",
                ),
            ),
            assembly_status=DecisionProjectionSection(
                source_object=release_package,
                source_field="assembly_package",
                source_value=release_package.assembly_package,
                meaning="Workshop-readable assembly content is present.",
                user_decision_supported="Workshop readiness",
            ),
            commercial_status=DecisionProjectionSection(
                source_object=commercial_report,
                source_field="estimated_price",
                source_value=commercial_report.estimated_price,
                meaning="Commercial boundary summary.",
                user_decision_supported="Quotation / release proceed",
            ),
            visualization_status=DecisionProjectionSection(
                source_object=production_package,
                source_field="production_evidence",
                source_value=production_package.production_evidence,
                meaning="Production-backed visualization is available.",
                user_decision_supported="Visual fidelity check",
            ),
            recommended_next_actions=(
                manufacturing_decision.recommended_action,
                "Review production evidence before production.",
            ),
            release_decision=DecisionProjectionSection(
                source_object=production_package,
                source_field="release_ready",
                source_value=production_package.release_ready,
                meaning="Production package readiness.",
                user_decision_supported="Release / hold",
            ),
        )

        self.assertIs(projection.readiness_summary.source_object, manufacturing_decision)
        self.assertEqual(
            projection.readiness_summary.source_value,
            manufacturing_decision.status,
        )
        self.assertIs(projection.blocking_issues[0].source_object, manufacturing_decision)
        self.assertEqual(
            projection.blocking_issues[0].source_value,
            manufacturing_decision.blocking_reasons,
        )
        self.assertIs(projection.blocking_issues[1].source_object, validation_summary)
        self.assertEqual(
            projection.warning_summary.source_value,
            manufacturing_decision.warning_reasons,
        )
        self.assertIs(
            projection.manufacturing_output_status[0].source_value,
            release_package.cut_list,
        )
        self.assertIs(
            projection.assembly_status.source_object,
            release_package,
        )
        self.assertIs(
            projection.commercial_status.source_object,
            commercial_report,
        )
        self.assertIs(
            projection.visualization_status.source_object,
            production_package,
        )
        self.assertEqual(
            projection.release_decision.source_value,
            production_package.release_ready,
        )

    def test_module_has_no_duplicate_decision_logic(self):
        source = inspect.getsource(projection_module)

        for token in (
            "ManufacturingDecisionBuilder",
            "ManufacturingValidationSummaryBuilder",
            "ManufacturingReleaseValidator",
            "CommercialPackageBuilder",
            "CostPackageBuilder",
            "validate(",
            "recommended_action =",
            "ready_for_production =",
            "blocking_reasons =",
            "warning_reasons =",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
