import importlib
import inspect
import unittest
from types import SimpleNamespace


class TestNestingProfitabilityContract(unittest.TestCase):
    def test_nesting_intelligence_consumes_sheet_utilization_and_offcut_intelligence(self):
        source = inspect.getsource(
            importlib.import_module("cost_intelligence.nesting_intelligence_builder")
        )

        self.assertIn("sheet_utilization_report", source)
        self.assertIn("offcut_intelligence_report", source)
        self.assertIn("waste_intelligence_report", source)

    def test_waste_intelligence_influences_optimization_result(self):
        source = inspect.getsource(
            importlib.import_module(
                "cost_intelligence.manufacturing_optimization_pipeline_builder"
            )
        )

        self.assertIn("waste_intelligence_report", source)
        self.assertIn("ManufacturingOptimizationResult", source)

    def test_optimization_result_must_influence_profitability_calculations(self):
        """Waste/sheet/recovery data flows through ManufacturingCostSummary
        to profitability, not directly into commercial builders."""
        source = inspect.getsource(
            importlib.import_module(
                "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder"
            )
        )

        self.assertIn("waste_intelligence_report", source)
        self.assertIn("offcut_intelligence_report", source)
        self.assertIn("sheet_cost", source)
        self.assertIn("recovered_value", source)

    def test_nesting_risk_influences_production_readiness(self):
        from cost_intelligence.production_readiness_builder import (
            ProductionReadinessBuilder,
        )

        report = ProductionReadinessBuilder().build(
            manufacturing_production_package=SimpleNamespace(
                release_ready=True,
                warnings=[],
            ),
            manufacturing_cost_summary=SimpleNamespace(
                risk_level="LOW",
                warnings=[],
                risk_report=None,
            ),
            manufacturing_optimization_result=SimpleNamespace(
                nesting_intelligence_report=SimpleNamespace(
                    risk_level="MEDIUM",
                    warnings=["Review nesting layout"],
                    recommendation="Review nesting layout for better sheet utilization",
                )
            ),
            manufacturing_commercial_result=SimpleNamespace(
                profitability_report=SimpleNamespace(
                    gross_profit=100.0,
                    warnings=[],
                )
            ),
        )

        self.assertEqual(report.status, "READY_WITH_WARNINGS")
        self.assertEqual(report.nesting_risk_level, "MEDIUM")
        self.assertIn("Review nesting layout", report.warnings)


if __name__ == "__main__":
    unittest.main()
