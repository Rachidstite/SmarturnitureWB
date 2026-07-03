import ast
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

OFFICIAL_ALLOWED_LAYER_FLOW = {
    "Engineering": ("Manufacturing",),
    "Manufacturing": ("Factory Operations", "Cost Intelligence"),
    "Factory Operations": ("Cost Intelligence",),
    "Cost Intelligence": ("Commercial Intelligence",),
    "Commercial Intelligence": ("Business Intelligence", "Commercial Outputs"),
    "Business Intelligence": ("Customer Outputs",),
    "Commercial Outputs": ("Customer Outputs",),
}

LEGACY_BRIDGE_WHITELIST = (
    "domain/base_cabinet_product_workflow.py",
    "cost_intelligence/furniture_project_quotation_builder.py",
    "cost_intelligence/furniture_project_quotation_breakdown_builder.py",
    "cost_intelligence/furniture_project_profitability_builder.py",
    "cost_intelligence/furniture_project_factory_decision_builder.py",
    "cost_intelligence/furniture_project_business_report_builder.py",
    "cost_intelligence/manufacturing_factory_intelligence_pipeline_builder.py",
    "cost_intelligence/factory_governance_runtime_service.py",
    "cost_intelligence/scene_graph_cost_service.py",
    "cost_intelligence/cost_package_builder.py",
)

COMMERCIAL_MODULES = (
    "cost_intelligence/manufacturing_quotation_input.py",
    "cost_intelligence/manufacturing_quotation_input_builder.py",
    "cost_intelligence/quotation_report.py",
    "cost_intelligence/quotation_calculator.py",
    "cost_intelligence/manufacturing_quotation_report_builder.py",
    "cost_intelligence/profitability_report.py",
    "cost_intelligence/profitability_calculator.py",
    "cost_intelligence/manufacturing_profitability_report_builder.py",
    "cost_intelligence/quotation_intelligence_report.py",
    "cost_intelligence/quotation_intelligence_builder.py",
    "cost_intelligence/quotation_breakdown_report.py",
    "cost_intelligence/quotation_breakdown_builder.py",
    "cost_intelligence/quotation_document.py",
    "cost_intelligence/quotation_document_builder.py",
    "cost_intelligence/commercial_acceptance_contract.py",
    "commercial_outputs/commercial_package_report.py",
    "commercial_outputs/commercial_package_builder.py",
)

BUSINESS_INTELLIGENCE_MODULES = (
    "cost_intelligence/manufacturing_kpi_report.py",
    "cost_intelligence/manufacturing_kpi_builder.py",
    "cost_intelligence/manufacturing_executive_report.py",
    "cost_intelligence/manufacturing_executive_report_builder.py",
    "cost_intelligence/factory_decision_report.py",
    "cost_intelligence/factory_decision_builder.py",
    "cost_intelligence/factory_decision_intelligence_builder.py",
    "cost_intelligence/factory_governance_state.py",
    "cost_intelligence/factory_governance_policy_context.py",
    "cost_intelligence/factory_governance_policy_report.py",
    "cost_intelligence/factory_governance_policy_builder.py",
    "cost_intelligence/factory_governance_authority_report.py",
    "cost_intelligence/factory_governance_authority_resolver.py",
    "cost_intelligence/factory_governance_recommendation_report.py",
    "cost_intelligence/factory_governance_recommendation_builder.py",
    "cost_intelligence/factory_governance_decision_report.py",
    "cost_intelligence/factory_governance_commercial_impact_report.py",
    "cost_intelligence/factory_governance_commercial_impact_builder.py",
    "cost_intelligence/manufacturing_factory_intelligence_result.py",
    "cost_intelligence/furniture_project_executive_report.py",
    "cost_intelligence/furniture_project_executive_report_builder.py",
    "cost_intelligence/furniture_project_business_report.py",
)

CUSTOMER_OUTPUT_MODULES = (
    "customer_outputs/customer_package_report.py",
    "customer_outputs/customer_package_builder.py",
)

FORBIDDEN_COMMERCIAL_IMPORT_PREFIXES = (
    "manufacturing",
    "project_engineering",
    "cost_intelligence.manufacturing_optimization_pipeline_builder",
    "cost_intelligence.manufacturing_optimization_result",
    "cost_intelligence.sheet_utilization_builder",
    "cost_intelligence.sheet_utilization_report",
    "cost_intelligence.offcut",
    "cost_intelligence.offcut_adapter",
    "cost_intelligence.offcut_classifier",
    "cost_intelligence.offcut_extraction_service",
    "cost_intelligence.offcut_intelligence_builder",
    "cost_intelligence.offcut_intelligence_report",
    "cost_intelligence.offcut_report",
    "cost_intelligence.offcut_report_builder",
    "cost_intelligence.offcut_reuse_policy",
    "cost_intelligence.waste_intelligence_builder",
    "cost_intelligence.waste_intelligence_report",
    "cost_intelligence.nesting_intelligence_builder",
    "cost_intelligence.nesting_intelligence_report",
)

FORBIDDEN_COMMERCIAL_NAMES = (
    "FactoryWorkloadBuilder",
    "ManufacturingRuntimePipelineBuilder",
    "ManufacturingCapacityBuilder",
    "ManufacturingDurationBuilder",
    "ManufacturingComplexityBuilder",
    "ProductionScheduleBuilder",
    "ManufacturingOptimizationPipelineBuilder",
    "SheetUtilizationBuilder",
    "ManufacturingOptimizationResult",
    "SheetUtilizationReport",
    "Offcut",
    "OffcutReport",
    "OffcutIntelligenceReport",
    "WasteIntelligenceReport",
    "NestingIntelligenceReport",
)

FORBIDDEN_BI_IMPORT_PREFIXES = (
    "manufacturing",
    "project_engineering",
    "cost_intelligence.manufacturing_optimization_pipeline_builder",
    "cost_intelligence.manufacturing_optimization_result",
    "cost_intelligence.sheet_utilization_builder",
    "cost_intelligence.sheet_utilization_report",
    "cost_intelligence.offcut",
    "cost_intelligence.offcut_adapter",
    "cost_intelligence.offcut_classifier",
    "cost_intelligence.offcut_extraction_service",
    "cost_intelligence.offcut_intelligence_builder",
    "cost_intelligence.offcut_intelligence_report",
    "cost_intelligence.offcut_report",
    "cost_intelligence.offcut_report_builder",
    "cost_intelligence.offcut_reuse_policy",
    "cost_intelligence.waste_intelligence_builder",
    "cost_intelligence.waste_intelligence_report",
    "cost_intelligence.nesting_intelligence_builder",
    "cost_intelligence.nesting_intelligence_report",
)

ALLOWED_CUSTOMER_OUTPUT_IMPORT_PREFIXES = (
    "commercial_outputs.commercial_package_report",
    "cost_intelligence.quotation_document",
    "customer_outputs.customer_package_report",
    "dataclasses",
)

FORBIDDEN_CUSTOMER_OUTPUT_IMPORT_PREFIXES = (
    "manufacturing",
    "project_engineering",
    "cost_intelligence.cost_package_report",
    "cost_intelligence.manufacturing_cost_summary",
    "cost_intelligence.manufacturing_cost_pipeline_builder",
    "cost_intelligence.manufacturing_cost_calculator",
    "cost_intelligence.manufacturing_cost_context",
    "cost_intelligence.manufacturing_cost_context_builder",
    "cost_intelligence.manufacturing_cost_insights",
    "cost_intelligence.manufacturing_cost_insights_builder",
    "cost_intelligence.manufacturing_cost_report",
    "cost_intelligence.manufacturing_cost_risk_report",
    "cost_intelligence.manufacturing_cost_risk_report_builder",
    "cost_intelligence.manufacturing_cost_rules",
    "cost_intelligence.manufacturing_cost_rules_builder",
    "cost_intelligence.factory_",
)


def _parse_module(relative_path):
    path = REPO_ROOT / relative_path
    source = path.read_text(encoding="utf-8")
    return path, source, ast.parse(source, filename=str(path))


def _imported_modules(tree):
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    return imported


def _referenced_identifiers(tree):
    identifiers = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            identifiers.add(node.id)
        elif isinstance(node, ast.Attribute):
            identifiers.add(node.attr)
    return identifiers


def _matches_prefix(module_name, prefix):
    return module_name == prefix or module_name.startswith(prefix + ".")


class TestLayerFlowContract(unittest.TestCase):
    def test_official_allowed_layer_flow_is_stable(self):
        self.assertEqual(
            OFFICIAL_ALLOWED_LAYER_FLOW,
            {
                "Engineering": ("Manufacturing",),
                "Manufacturing": ("Factory Operations", "Cost Intelligence"),
                "Factory Operations": ("Cost Intelligence",),
                "Cost Intelligence": ("Commercial Intelligence",),
                "Commercial Intelligence": ("Business Intelligence", "Commercial Outputs"),
                "Business Intelligence": ("Customer Outputs",),
                "Commercial Outputs": ("Customer Outputs",),
            },
        )

    def test_legacy_bridge_whitelist_is_exact_and_complete(self):
        self.assertEqual(
            LEGACY_BRIDGE_WHITELIST,
            (
                "domain/base_cabinet_product_workflow.py",
                "cost_intelligence/furniture_project_quotation_builder.py",
                "cost_intelligence/furniture_project_quotation_breakdown_builder.py",
                "cost_intelligence/furniture_project_profitability_builder.py",
                "cost_intelligence/furniture_project_factory_decision_builder.py",
                "cost_intelligence/furniture_project_business_report_builder.py",
                "cost_intelligence/manufacturing_factory_intelligence_pipeline_builder.py",
                "cost_intelligence/factory_governance_runtime_service.py",
                "cost_intelligence/scene_graph_cost_service.py",
                "cost_intelligence/cost_package_builder.py",
            ),
        )

        for relative_path in LEGACY_BRIDGE_WHITELIST:
            self.assertTrue(
                (REPO_ROOT / relative_path).exists(),
                msg=f"Whitelisted legacy bridge is missing: {relative_path}",
            )

    def test_logical_commercial_modules_do_not_bypass_lower_layers(self):
        for relative_path in COMMERCIAL_MODULES:
            _, _, tree = _parse_module(relative_path)
            imported_modules = _imported_modules(tree)
            identifiers = _referenced_identifiers(tree)

            for forbidden_prefix in FORBIDDEN_COMMERCIAL_IMPORT_PREFIXES:
                offenders = sorted(
                    module
                    for module in imported_modules
                    if _matches_prefix(module, forbidden_prefix)
                )
                self.assertFalse(
                    offenders,
                    msg=(
                        f"Commercial module {relative_path} bypasses allowed flow via "
                        f"{forbidden_prefix}: {offenders}"
                    ),
                )

            for forbidden_name in FORBIDDEN_COMMERCIAL_NAMES:
                self.assertNotIn(
                    forbidden_name,
                    identifiers,
                    msg=(
                        f"Commercial module {relative_path} references forbidden lower-layer "
                        f"runtime or optimization object {forbidden_name}"
                    ),
                )

    def test_business_intelligence_modules_do_not_consume_runtime_layers(self):
        for relative_path in BUSINESS_INTELLIGENCE_MODULES:
            _, _, tree = _parse_module(relative_path)
            imported_modules = _imported_modules(tree)

            for forbidden_prefix in FORBIDDEN_BI_IMPORT_PREFIXES:
                offenders = sorted(
                    module
                    for module in imported_modules
                    if _matches_prefix(module, forbidden_prefix)
                )
                self.assertFalse(
                    offenders,
                    msg=(
                        f"Business Intelligence module {relative_path} imports forbidden "
                        f"runtime dependency {forbidden_prefix}: {offenders}"
                    ),
                )

    def test_customer_output_modules_only_consume_allowed_output_contracts(self):
        for relative_path in CUSTOMER_OUTPUT_MODULES:
            _, _, tree = _parse_module(relative_path)
            imported_modules = _imported_modules(tree)

            for forbidden_prefix in FORBIDDEN_CUSTOMER_OUTPUT_IMPORT_PREFIXES:
                offenders = sorted(
                    module
                    for module in imported_modules
                    if _matches_prefix(module, forbidden_prefix)
                )
                self.assertFalse(
                    offenders,
                    msg=(
                        f"Customer output module {relative_path} imports forbidden upstream "
                        f"dependency {forbidden_prefix}: {offenders}"
                    ),
                )

            unexpected = sorted(
                module
                for module in imported_modules
                if module
                and not any(
                    _matches_prefix(module, allowed_prefix)
                    for allowed_prefix in ALLOWED_CUSTOMER_OUTPUT_IMPORT_PREFIXES
                )
            )
            self.assertFalse(
                unexpected,
                msg=(
                    f"Customer output module {relative_path} imports contracts outside the "
                    f"allowed output surface: {unexpected}"
                ),
            )


if __name__ == "__main__":
    unittest.main()
