import ast
import importlib
import unittest
from dataclasses import is_dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

BI_MODULES = (
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
    "cost_intelligence/factory_governance_runtime_service.py",
    "cost_intelligence/furniture_project_executive_report.py",
    "cost_intelligence/furniture_project_executive_report_builder.py",
    "cost_intelligence/furniture_project_business_report.py",
    "cost_intelligence/furniture_project_business_report_builder.py",
    "cost_intelligence/furniture_project_factory_decision_builder.py",
    "cost_intelligence/manufacturing_factory_intelligence_result.py",
    "cost_intelligence/manufacturing_factory_intelligence_pipeline_builder.py",
)

BI_LEGACY_WHITELIST = (
    "cost_intelligence/manufacturing_kpi_builder.py",
    "cost_intelligence/manufacturing_executive_report_builder.py",
    "cost_intelligence/factory_decision_builder.py",
    "cost_intelligence/factory_decision_intelligence_builder.py",
    "cost_intelligence/factory_governance_commercial_impact_builder.py",
    "cost_intelligence/factory_governance_runtime_service.py",
    "cost_intelligence/furniture_project_business_report_builder.py",
    "cost_intelligence/furniture_project_factory_decision_builder.py",
    "cost_intelligence/manufacturing_factory_intelligence_pipeline_builder.py",
    "cost_intelligence/manufacturing_factory_intelligence_result.py",
)

FORBIDDEN_FUTURE_BI_IMPORTS = (
    "manufacturing",
    "project_engineering",
    "exports.nesting_engine",
    "cost_intelligence.manufacturing_cost_calculator",
    "cost_intelligence.manufacturing_cost_pipeline_builder",
    "cost_intelligence.project_cost_calculator",
    "cost_intelligence.material_cost_calculator",
    "cost_intelligence.sheet_cost_calculator",
    "cost_intelligence.waste_cost_calculator",
    "cost_intelligence.hardware_cost_calculator",
    "cost_intelligence.cost_summary_calculator",
    "cost_intelligence.cost_package_report",
    "cost_intelligence.cost_package_builder",
    "cost_intelligence.manufacturing_commercial_result",
    "cost_intelligence.manufacturing_commercial_pipeline_builder",
    "cost_intelligence.quotation_report",
    "cost_intelligence.profitability_report",
    "cost_intelligence.quotation_intelligence_report",
    "cost_intelligence.quotation_breakdown_report",
    "cost_intelligence.manufacturing_quotation_input",
    "cost_intelligence.manufacturing_quotation_input_builder",
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

PASSIVE_BI_BOUNDARY_MODULES = (
    ("cost_intelligence.manufacturing_kpi_report", "ManufacturingKPIReport"),
    ("cost_intelligence.manufacturing_executive_report", "ManufacturingExecutiveReport"),
    ("cost_intelligence.factory_decision_report", "FactoryDecisionReport"),
    ("cost_intelligence.factory_governance_state", "FactoryGovernanceState"),
    ("cost_intelligence.factory_governance_policy_context", "FactoryGovernancePolicyContext"),
    ("cost_intelligence.factory_governance_policy_report", "FactoryGovernancePolicyReport"),
    ("cost_intelligence.factory_governance_authority_report", "FactoryGovernanceAuthorityReport"),
    ("cost_intelligence.factory_governance_recommendation_report", "FactoryGovernanceRecommendationReport"),
    ("cost_intelligence.factory_governance_decision_report", "FactoryGovernanceDecisionReport"),
    ("cost_intelligence.factory_governance_commercial_impact_report", "FactoryGovernanceCommercialImpactReport"),
    ("cost_intelligence.furniture_project_executive_report", "FurnitureProjectExecutiveReport"),
    ("cost_intelligence.furniture_project_business_report", "FurnitureProjectBusinessReport"),
)

APPROVED_FUTURE_COMMERCIAL_TO_BI_INPUT = (
    "commercial_outputs.commercial_package_report",
    "CommercialPackageReport",
)

DISALLOWED_FUTURE_PUBLIC_COMMERCIAL_TO_BI_INPUT = (
    "cost_intelligence.manufacturing_commercial_result",
    "ManufacturingCommercialResult",
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


def _matches_prefix(module_name, prefix):
    return module_name == prefix or module_name.startswith(prefix + ".")


class TestBusinessIntelligenceBoundaryContract(unittest.TestCase):
    def test_bi_module_set_is_explicit_and_stable(self):
        self.assertEqual(
            BI_MODULES,
            (
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
                "cost_intelligence/factory_governance_runtime_service.py",
                "cost_intelligence/furniture_project_executive_report.py",
                "cost_intelligence/furniture_project_executive_report_builder.py",
                "cost_intelligence/furniture_project_business_report.py",
                "cost_intelligence/furniture_project_business_report_builder.py",
                "cost_intelligence/furniture_project_factory_decision_builder.py",
                "cost_intelligence/manufacturing_factory_intelligence_result.py",
                "cost_intelligence/manufacturing_factory_intelligence_pipeline_builder.py",
            ),
        )

    def test_bi_legacy_whitelist_is_explicit_exact_and_exists(self):
        self.assertEqual(
            BI_LEGACY_WHITELIST,
            (
                "cost_intelligence/manufacturing_kpi_builder.py",
                "cost_intelligence/manufacturing_executive_report_builder.py",
                "cost_intelligence/factory_decision_builder.py",
                "cost_intelligence/factory_decision_intelligence_builder.py",
                "cost_intelligence/factory_governance_commercial_impact_builder.py",
                "cost_intelligence/factory_governance_runtime_service.py",
                "cost_intelligence/furniture_project_business_report_builder.py",
                "cost_intelligence/furniture_project_factory_decision_builder.py",
                "cost_intelligence/manufacturing_factory_intelligence_pipeline_builder.py",
                "cost_intelligence/manufacturing_factory_intelligence_result.py",
            ),
        )

        for relative_path in BI_LEGACY_WHITELIST:
            self.assertTrue(
                (REPO_ROOT / relative_path).exists(),
                msg=f"Whitelisted BI legacy bridge is missing: {relative_path}",
            )

    def test_non_whitelisted_bi_modules_do_not_import_forbidden_future_dependencies(self):
        for relative_path in BI_MODULES:
            if relative_path in BI_LEGACY_WHITELIST:
                continue

            _, _, tree = _parse_module(relative_path)
            imported_modules = _imported_modules(tree)

            for forbidden_import in FORBIDDEN_FUTURE_BI_IMPORTS:
                offenders = sorted(
                    module
                    for module in imported_modules
                    if _matches_prefix(module, forbidden_import)
                )
                self.assertFalse(
                    offenders,
                    msg=(
                        f"Non-whitelisted BI module {relative_path} imports forbidden "
                        f"future BI dependency {forbidden_import}: {offenders}"
                    ),
                )

    def test_non_whitelisted_bi_passive_boundary_objects_do_not_import_runtime_layers(self):
        for module_name, symbol_name in PASSIVE_BI_BOUNDARY_MODULES:
            module = importlib.import_module(module_name)
            contract_type = getattr(module, symbol_name)
            self.assertTrue(
                is_dataclass(contract_type) or symbol_name == "FactoryGovernanceState",
                msg=f"{symbol_name} should remain a passive BI contract",
            )

        for relative_path in (
            "cost_intelligence/manufacturing_kpi_report.py",
            "cost_intelligence/manufacturing_executive_report.py",
            "cost_intelligence/factory_decision_report.py",
            "cost_intelligence/factory_governance_state.py",
            "cost_intelligence/factory_governance_policy_context.py",
            "cost_intelligence/factory_governance_policy_report.py",
            "cost_intelligence/factory_governance_authority_report.py",
            "cost_intelligence/factory_governance_recommendation_report.py",
            "cost_intelligence/factory_governance_decision_report.py",
            "cost_intelligence/factory_governance_commercial_impact_report.py",
            "cost_intelligence/furniture_project_executive_report.py",
            "cost_intelligence/furniture_project_business_report.py",
        ):
            _, _, tree = _parse_module(relative_path)
            imported_modules = _imported_modules(tree)
            for forbidden_import in FORBIDDEN_FUTURE_BI_IMPORTS:
                offenders = sorted(
                    module
                    for module in imported_modules
                    if _matches_prefix(module, forbidden_import)
                )
                self.assertFalse(
                    offenders,
                    msg=(
                        f"Passive BI module {relative_path} imports forbidden runtime "
                        f"dependency {forbidden_import}: {offenders}"
                    ),
                )

    def test_commercial_package_report_is_the_approved_future_commercial_to_bi_input(self):
        module_name, symbol_name = APPROVED_FUTURE_COMMERCIAL_TO_BI_INPUT
        module = importlib.import_module(module_name)
        contract_type = getattr(module, symbol_name)
        self.assertEqual(contract_type.__name__, "CommercialPackageReport")
        self.assertTrue(is_dataclass(contract_type))

    def test_manufacturing_commercial_result_is_not_an_approved_future_public_bi_input(self):
        module_name, symbol_name = DISALLOWED_FUTURE_PUBLIC_COMMERCIAL_TO_BI_INPUT
        module = importlib.import_module(module_name)
        contract_type = getattr(module, symbol_name)
        self.assertEqual(contract_type.__name__, "ManufacturingCommercialResult")
        self.assertTrue(is_dataclass(contract_type))
        self.assertNotEqual(
            module_name,
            APPROVED_FUTURE_COMMERCIAL_TO_BI_INPUT[0],
            msg="ManufacturingCommercialResult must not become the approved future BI input",
        )


if __name__ == "__main__":
    unittest.main()
