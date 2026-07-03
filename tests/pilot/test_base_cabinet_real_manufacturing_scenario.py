import unittest
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
from application.manufacturing_application_service import (
    ManufacturingApplicationService,
)
from commercial_outputs.commercial_package_builder import CommercialPackageBuilder
from commercial_outputs.commercial_package_report import CommercialPackageReport
from core.material_manager import MaterialManager
from cost_intelligence.cost_package_builder import CostPackageBuilder
from cost_intelligence.cost_package_report import CostPackageReport
from cost_intelligence.quotation_document import QuotationDocumentV1
from domain.base_cabinet_product_workflow import (
    build_base_cabinet_product_workflow,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from engine.cabinet import Cabinet
from engine.geometry_engine import GeometryEngine
from manufacturing.factory_decision_projection import (
    DecisionProjectionSection,
    FactoryDecisionProjection,
)
from manufacturing.factory_release_package import FactoryReleasePackage
from manufacturing.manufacturing_decision import ManufacturingDecision
from scene_graph.builder import SceneGraphBuilder


class _IntegrationCabinetBuilder:
    """Test-only stand-in for unavailable FreeCAD-bound CabinetBuilder."""

    def __init__(self):
        self.scene_graph = None

    def build(self, cabinet):
        material_manager = MaterialManager()
        geometry_engine = GeometryEngine(cabinet, material_manager)
        geometry_engine.resolve_all()
        self.scene_graph = SceneGraphBuilder(
            cabinet,
            material_manager,
        ).build(geometry_engine)
        cabinet.graph = self.scene_graph
        cabinet.scene_graph = self.scene_graph


class TestBaseCabinetRealManufacturingScenario(unittest.TestCase):
    def _specification(self):
        return BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=560.0,
            door_count=2,
            shelf_count=1,
            has_back_panel=True,
            edge_banding_required=True,
            toe_kick_required=True,
            hinge_family="STANDARD_110",
            drawer_family="NONE",
        )

    def _build_projection(
        self,
        *,
        manufacturing_decision,
        validation_summary,
        production_package,
        release_package,
        commercial_report,
        quotation_document,
    ):
        return FactoryDecisionProjection(
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
                source_object=production_package.production_evidence,
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

    def test_real_base_cabinet_scenario_runs_end_to_end(self):
        specification = self._specification()
        quotation_metadata = {
            "quotation_number": "Q-2026-BASE-001",
            "issue_date": "2026-07-03",
            "valid_until": "2026-08-03",
            "seller_name": "Smart Furniture",
            "customer_name": "Pilot Customer",
            "project_description": "600mm base cabinet pilot scenario",
            "notes": "Pilot scenario for release validation.",
            "payment_terms": "30% deposit",
        }

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=_IntegrationCabinetBuilder,
        ):
            product_result = build_base_cabinet_product_workflow(
                specification,
                quotation_metadata=quotation_metadata,
            )
            manufacturing_result = ManufacturingApplicationService().execute(
                specification=specification
            )

        self.assertIsInstance(product_result.engineering, Cabinet)
        self.assertIsNotNone(product_result.engineering.engineering_model)
        self.assertIsNotNone(product_result.engineering.scene_graph)

        self.assertIsNotNone(product_result.manufacturing_outputs)
        self.assertIsNotNone(product_result.manufacturing_outputs.cut_list)
        self.assertIsNotNone(
            product_result.manufacturing_outputs.manufacturing_package
        )

        self.assertIsNotNone(product_result.cost)
        self.assertIsNotNone(product_result.cost.manufacturing_cost_summary)
        self.assertIsNotNone(
            product_result.cost.manufacturing_cost_summary.cost_report
        )

        factory_release_package = manufacturing_result.data["factory_release_package"]
        self.assertIsInstance(factory_release_package, FactoryReleasePackage)
        self.assertIsInstance(
            factory_release_package.manufacturing_decision,
            ManufacturingDecision,
        )
        self.assertIs(factory_release_package.cut_list, manufacturing_result.data["cut_list"])
        self.assertIs(
            factory_release_package.hardware_bom,
            manufacturing_result.data["manufacturing_production_package"].hardware_report,
        )
        self.assertIs(
            factory_release_package.cnc_package,
            manufacturing_result.data["manufacturing_production_package"].cnc_report,
        )
        self.assertIs(
            factory_release_package.assembly_package,
            manufacturing_result.data["manufacturing_production_package"].assembly_report,
        )
        self.assertEqual(
            factory_release_package.warnings,
            manufacturing_result.data["manufacturing_production_package"].warnings,
        )

        cost_report = CostPackageBuilder().build(factory_release_package)
        self.assertIsInstance(cost_report, CostPackageReport)

        commercial_report = CommercialPackageBuilder().build(cost_report)
        self.assertIsInstance(commercial_report, CommercialPackageReport)

        self.assertIsInstance(product_result.quotation_document, QuotationDocumentV1)
        self.assertIsNotNone(product_result.commercial)
        self.assertIsNotNone(product_result.commercial.commercial_result)

        production_package = manufacturing_result.data["manufacturing_production_package"]
        self.assertTrue(production_package.has_cutlist_evidence)
        self.assertTrue(production_package.has_machining_evidence)
        self.assertTrue(production_package.has_edge_evidence)
        self.assertTrue(production_package.has_hardware_evidence)
        self.assertGreater(
            len(getattr(production_package.hardware_report, "bom_rows", []) or []),
            0,
        )
        self.assertGreater(
            len(getattr(production_package.assembly_report, "rows", []) or []),
            0,
        )
        self.assertNotIn(
            "No materials",
            manufacturing_result.data["manufacturing_decision"].warning_reasons,
        )
        self.assertTrue(
            len(getattr(production_package.assembly_report, "rows", []) or [])
            >= len(getattr(production_package.hardware_report, "bom_rows", []) or []),
            "Assembly documentation should be driven by hardware evidence.",
        )

        validation_summary = product_result.validation.manufacturing_validation_summary_report
        self.assertIsNotNone(validation_summary)
        self.assertGreaterEqual(validation_summary.total_rule_count, 0)

        projection = self._build_projection(
            manufacturing_decision=factory_release_package.manufacturing_decision,
            validation_summary=validation_summary,
            production_package=production_package,
            release_package=factory_release_package,
            commercial_report=commercial_report,
            quotation_document=product_result.quotation_document,
        )

        self.assertIsInstance(projection, FactoryDecisionProjection)
        self.assertIs(
            projection.readiness_summary.source_object,
            factory_release_package.manufacturing_decision,
        )
        self.assertEqual(
            projection.readiness_summary.source_value,
            factory_release_package.manufacturing_decision.status,
        )
        self.assertEqual(
            projection.blocking_issues[0].source_value,
            factory_release_package.manufacturing_decision.blocking_reasons,
        )
        self.assertEqual(
            projection.warning_summary.source_value,
            factory_release_package.manufacturing_decision.warning_reasons,
        )
        self.assertIs(
            projection.manufacturing_output_status[0].source_value,
            factory_release_package.cut_list,
        )
        self.assertIs(
            projection.assembly_status.source_value,
            factory_release_package.assembly_package,
        )
        self.assertEqual(
            projection.commercial_status.source_value,
            commercial_report.estimated_price,
        )
        self.assertEqual(
            projection.visualization_status.source_value,
            production_package.production_evidence,
        )
        self.assertEqual(
            projection.release_decision.source_value,
            production_package.release_ready,
        )
        self.assertTrue(projection.recommended_next_actions)

        self.assertIn("factory_release_package", manufacturing_result.data)
        self.assertIn("manufacturing_production_package", manufacturing_result.data)
        self.assertIn("manufacturing_decision", manufacturing_result.data)
        self.assertIn("metadata", manufacturing_result.data)
        self.assertIn("specification", manufacturing_result.data)


if __name__ == "__main__":
    unittest.main()
