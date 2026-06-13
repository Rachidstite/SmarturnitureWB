import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestProductionReadinessBuilder(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.production_readiness_builder import (
            ProductionReadinessBuilder,
        )

        self.builder = ProductionReadinessBuilder()

    def test_report_is_dataclass_with_required_fields(self):
        from cost_intelligence.production_readiness_report import (
            ProductionReadinessReport,
        )

        self.assertTrue(is_dataclass(ProductionReadinessReport))
        self.assertEqual(
            [field.name for field in fields(ProductionReadinessReport)],
            [
                "status",
                "manufacturing_ready",
                "cost_risk_level",
                "nesting_risk_level",
                "profitability_ok",
                "blocking_issues",
                "warnings",
                "recommendations",
            ],
        )

    def test_ready_when_all_conditions_are_clear(self):
        report = self.builder.build(*self._inputs())

        self.assertEqual(report.status, "READY")
        self.assertTrue(report.manufacturing_ready)
        self.assertEqual(report.cost_risk_level, "LOW")
        self.assertEqual(report.nesting_risk_level, "LOW")
        self.assertTrue(report.profitability_ok)
        self.assertEqual(report.blocking_issues, [])
        self.assertEqual(report.warnings, [])

    def test_each_blocking_condition_creates_blocking_issue(self):
        package, cost_summary, optimization_result, commercial_result = (
            self._inputs()
        )
        package.release_ready = False
        cost_summary.risk_level = "HIGH"
        commercial_result.profitability_report.gross_profit = 0

        report = self.builder.build(
            package,
            cost_summary,
            optimization_result,
            commercial_result,
        )

        self.assertEqual(report.status, "BLOCKED")
        self.assertFalse(report.manufacturing_ready)
        self.assertFalse(report.profitability_ok)
        self.assertEqual(
            report.blocking_issues,
            [
                "Manufacturing production package is not release ready",
                "Manufacturing cost risk is HIGH",
                "Profitability is not positive",
            ],
        )

    def test_warnings_make_ready_with_warnings(self):
        package, cost_summary, optimization_result, commercial_result = (
            self._inputs()
        )
        package.warnings = ["Package warning"]
        cost_summary.warnings = ["Cost warning"]
        optimization_result.nesting_intelligence_report.warnings = [
            "Nesting warning"
        ]
        commercial_result.profitability_report.warnings = [
            "Profitability warning"
        ]

        report = self.builder.build(
            package,
            cost_summary,
            optimization_result,
            commercial_result,
        )

        self.assertEqual(report.status, "READY_WITH_WARNINGS")
        self.assertEqual(
            report.warnings,
            [
                "Package warning",
                "Cost warning",
                "Nesting warning",
                "Profitability warning",
            ],
        )
        self.assertIsNot(report.warnings, package.warnings)

    def test_medium_nesting_risk_makes_ready_with_warnings(self):
        package, cost_summary, optimization_result, commercial_result = (
            self._inputs()
        )
        optimization_result.nesting_intelligence_report.risk_level = "MEDIUM"

        report = self.builder.build(
            package,
            cost_summary,
            optimization_result,
            commercial_result,
        )

        self.assertEqual(report.status, "READY_WITH_WARNINGS")
        self.assertEqual(report.blocking_issues, [])

    def test_builder_carries_existing_recommendations_without_mutating_inputs(self):
        package, cost_summary, optimization_result, commercial_result = (
            self._inputs()
        )
        package_warnings = package.warnings
        cost_summary.risk_report = SimpleNamespace(
            recommendation="Review manufacturing cost risk"
        )
        optimization_result.nesting_intelligence_report.recommendation = (
            "Review nesting layout"
        )

        report = self.builder.build(
            package,
            cost_summary,
            optimization_result,
            commercial_result,
        )

        self.assertEqual(
            report.recommendations,
            [
                "Review manufacturing cost risk",
                "Review nesting layout",
            ],
        )
        self.assertIs(package.warnings, package_warnings)

    @staticmethod
    def _inputs():
        from cost_intelligence.manufacturing_commercial_result import (
            ManufacturingCommercialResult,
        )
        from cost_intelligence.manufacturing_cost_summary import (
            ManufacturingCostSummary,
        )
        from cost_intelligence.manufacturing_optimization_result import (
            ManufacturingOptimizationResult,
        )
        from cost_intelligence.nesting_intelligence_report import (
            NestingIntelligenceReport,
        )
        from cost_intelligence.profitability_report import ProfitabilityReport
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        package = ManufacturingProductionPackage(release_ready=True)
        cost_summary = ManufacturingCostSummary(risk_level="LOW")
        nesting_report = NestingIntelligenceReport(risk_level="LOW")
        optimization_result = ManufacturingOptimizationResult(
            sheet_utilization_report=object(),
            offcut_report=object(),
            offcut_intelligence_report=object(),
            waste_intelligence_report=object(),
            nesting_intelligence_report=nesting_report,
        )
        commercial_result = ManufacturingCommercialResult(
            manufacturing_cost_summary=cost_summary,
            manufacturing_quotation_input=object(),
            quotation_report=object(),
            profitability_report=ProfitabilityReport(gross_profit=1.0),
        )
        return package, cost_summary, optimization_result, commercial_result


if __name__ == "__main__":
    unittest.main()
