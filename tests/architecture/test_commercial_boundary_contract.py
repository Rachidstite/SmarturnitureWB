import ast
import importlib
import unittest
from dataclasses import is_dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

OFFICIAL_BOUNDARY_IMPORTS = (
    ("cost_intelligence.manufacturing_cost_summary", "ManufacturingCostSummary"),
    ("cost_intelligence.cost_package_report", "CostPackageReport"),
)

COMMERCIAL_COMPONENTS = {
    "ManufacturingQuotationInput": "cost_intelligence/manufacturing_quotation_input.py",
    "ManufacturingQuotationInputBuilder": "cost_intelligence/manufacturing_quotation_input_builder.py",
    "QuotationReport": "cost_intelligence/quotation_report.py",
    "QuotationCalculator": "cost_intelligence/quotation_calculator.py",
    "ManufacturingQuotationReportBuilder": "cost_intelligence/manufacturing_quotation_report_builder.py",
    "ProfitabilityReport": "cost_intelligence/profitability_report.py",
    "ProfitabilityCalculator": "cost_intelligence/profitability_calculator.py",
    "ManufacturingProfitabilityReportBuilder": "cost_intelligence/manufacturing_profitability_report_builder.py",
    "QuotationIntelligenceReport": "cost_intelligence/quotation_intelligence_report.py",
    "QuotationIntelligenceBuilder": "cost_intelligence/quotation_intelligence_builder.py",
    "QuotationBreakdownReport": "cost_intelligence/quotation_breakdown_report.py",
    "QuotationBreakdownBuilder": "cost_intelligence/quotation_breakdown_builder.py",
    "QuotationDocumentV1": "cost_intelligence/quotation_document.py",
    "QuotationDocumentBuilderV1": "cost_intelligence/quotation_document_builder.py",
    "CommercialAcceptanceContract": "cost_intelligence/commercial_acceptance_contract.py",
    "CommercialPackageReport": "commercial_outputs/commercial_package_report.py",
    "CommercialPackageBuilder": "commercial_outputs/commercial_package_builder.py",
}

COMMERCIAL_MODULE_PATHS = tuple(sorted(set(COMMERCIAL_COMPONENTS.values())))

FORBIDDEN_UPSTREAM_PACKAGES = (
    "manufacturing",
    "project_engineering",
    "exports.nesting_engine",
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
    "cost_intelligence.factory_governance_runtime_service",
    "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder",
    "cost_intelligence.manufacturing_kpi_builder",
    "cost_intelligence.manufacturing_executive_report_builder",
    "cost_intelligence.factory_decision_builder",
    "cost_intelligence.furniture_project_business_report_builder",
)

FORBIDDEN_MANUFACTURING_BUILDERS = (
    "ManufacturingProductionPackageBuilder",
    "ManufacturingRuntimePipelineBuilder",
    "ManufacturingMetricsBuilder",
    "ManufacturingCapacityBuilder",
    "ManufacturingDurationBuilder",
    "ManufacturingComplexityBuilder",
    "FactoryWorkloadBuilder",
    "ProductionScheduleBuilder",
)

FORBIDDEN_OPTIMIZATION_REFERENCES = (
    "ManufacturingOptimizationResult",
    "ManufacturingOptimizationPipelineBuilder",
    "SheetUtilizationReport",
    "SheetUtilizationBuilder",
    "Offcut",
    "OffcutReport",
    "OffcutIntelligenceReport",
    "WasteIntelligenceReport",
    "NestingIntelligenceReport",
)

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

PASSIVE_COMMERCIAL_CONTRACTS = (
    ("cost_intelligence.manufacturing_quotation_input", "ManufacturingQuotationInput"),
    ("cost_intelligence.quotation_report", "QuotationReport"),
    ("cost_intelligence.profitability_report", "ProfitabilityReport"),
    ("cost_intelligence.quotation_intelligence_report", "QuotationIntelligenceReport"),
    ("cost_intelligence.quotation_breakdown_report", "QuotationBreakdownReport"),
    ("cost_intelligence.quotation_document", "QuotationDocumentV1"),
    ("cost_intelligence.commercial_acceptance_contract", "CommercialAcceptanceContract"),
    ("commercial_outputs.commercial_package_report", "CommercialPackageReport"),
)


def _parse_module(path_str):
    path = REPO_ROOT / path_str
    source = path.read_text(encoding="utf-8")
    return path, source, ast.parse(source, filename=str(path))


def _iter_import_records(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, alias.name.split(".")[0], alias.asname
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                yield module, alias.name, alias.asname


def _imported_modules(tree):
    return {module for module, _, _ in _iter_import_records(tree)}


def _imported_names(tree):
    names = set()
    for _, imported_name, alias in _iter_import_records(tree):
        names.add(imported_name)
        if alias:
            names.add(alias)
    return names


def _referenced_identifiers(tree):
    identifiers = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            identifiers.add(node.id)
        elif isinstance(node, ast.Attribute):
            identifiers.add(node.attr)
    return identifiers


def _is_forbidden_module(imported_module, forbidden_module):
    return imported_module == forbidden_module or imported_module.startswith(
        forbidden_module + "."
    )


class TestCommercialBoundaryContract(unittest.TestCase):
    def test_official_commercial_boundary_inputs_are_importable(self):
        imported = []
        for module_name, symbol_name in OFFICIAL_BOUNDARY_IMPORTS:
            module = importlib.import_module(module_name)
            imported.append(getattr(module, symbol_name).__name__)

        self.assertEqual(
            imported,
            ["ManufacturingCostSummary", "CostPackageReport"],
        )

    def test_logical_commercial_components_do_not_import_forbidden_upstreams(self):
        for component_name, module_path in COMMERCIAL_COMPONENTS.items():
            _, _, tree = _parse_module(module_path)
            imported_modules = _imported_modules(tree)

            for forbidden_module in FORBIDDEN_UPSTREAM_PACKAGES:
                offenders = sorted(
                    module
                    for module in imported_modules
                    if _is_forbidden_module(module, forbidden_module)
                )
                self.assertFalse(
                    offenders,
                    msg=(
                        f"{component_name} in {module_path} imports forbidden upstream "
                        f"{forbidden_module}: {offenders}"
                    ),
                )

    def test_logical_commercial_components_do_not_import_manufacturing_builders(self):
        for component_name, module_path in COMMERCIAL_COMPONENTS.items():
            _, _, tree = _parse_module(module_path)
            imported_names = _imported_names(tree)

            for forbidden_name in FORBIDDEN_MANUFACTURING_BUILDERS:
                self.assertNotIn(
                    forbidden_name,
                    imported_names,
                    msg=(
                        f"{component_name} in {module_path} imports forbidden builder "
                        f"{forbidden_name}"
                    ),
                )

    def test_legacy_bridge_whitelist_is_documented_and_exists(self):
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
                msg=f"Legacy bridge whitelist entry does not exist: {relative_path}",
            )

    def test_logical_commercial_components_do_not_reference_optimization_objects(self):
        for component_name, module_path in COMMERCIAL_COMPONENTS.items():
            _, _, tree = _parse_module(module_path)
            referenced_identifiers = _referenced_identifiers(tree)

            for forbidden_name in FORBIDDEN_OPTIMIZATION_REFERENCES:
                self.assertNotIn(
                    forbidden_name,
                    referenced_identifiers,
                    msg=(
                        f"{component_name} in {module_path} references forbidden "
                        f"optimization object {forbidden_name}"
                    ),
                )

    def test_passive_commercial_boundary_objects_are_dataclass_like_and_isolated(self):
        for module_name, symbol_name in PASSIVE_COMMERCIAL_CONTRACTS:
            module = importlib.import_module(module_name)
            contract_type = getattr(module, symbol_name)
            self.assertTrue(
                is_dataclass(contract_type),
                msg=f"{symbol_name} should remain a passive dataclass-like contract",
            )

        forbidden_contract_modules = (
            "manufacturing",
            "project_engineering",
            "exports.nesting_engine",
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
            "cost_intelligence.factory_governance_runtime_service",
        )

        for module_path in (
            "cost_intelligence/manufacturing_quotation_input.py",
            "cost_intelligence/quotation_report.py",
            "cost_intelligence/profitability_report.py",
            "cost_intelligence/quotation_intelligence_report.py",
            "cost_intelligence/quotation_breakdown_report.py",
            "cost_intelligence/quotation_document.py",
            "cost_intelligence/commercial_acceptance_contract.py",
            "commercial_outputs/commercial_package_report.py",
        ):
            _, _, tree = _parse_module(module_path)
            imported_modules = _imported_modules(tree)
            for forbidden_module in forbidden_contract_modules:
                offenders = sorted(
                    module
                    for module in imported_modules
                    if _is_forbidden_module(module, forbidden_module)
                )
                self.assertFalse(
                    offenders,
                    msg=(
                        f"Passive commercial contract module {module_path} imports "
                        f"forbidden dependency {forbidden_module}: {offenders}"
                    ),
                )


if __name__ == "__main__":
    unittest.main()
