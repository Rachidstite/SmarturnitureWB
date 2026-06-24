import unittest
from dataclasses import is_dataclass
from types import SimpleNamespace


class TestManufacturingOptimizationPipelineContract(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.manufacturing_optimization_pipeline_builder import (
            ManufacturingOptimizationPipelineBuilder,
        )

        self.builder = ManufacturingOptimizationPipelineBuilder()

    def test_pipeline_builds_all_existing_reports_and_preserves_inputs(self):
        sheet_results = [
            SimpleNamespace(
                sheet_width=100,
                sheet_height=50,
                used_area=2500,
            ),
            SimpleNamespace(
                sheet_width=200,
                sheet_height=50,
                used_area=5000,
            ),
        ]
        consumption_report = SimpleNamespace(
            waste_ratio=0.20,
            warnings=["Consumption warning"],
        )
        cost_estimate = SimpleNamespace(
            waste_cost=88.0,
            warnings=["Cost warning"],
        )

        sheet_results_snapshot = self._snapshot(sheet_results)
        consumption_snapshot = self._snapshot(consumption_report)
        cost_snapshot = self._snapshot(cost_estimate)

        result = self.builder.build(
            sheet_results,
            consumption_report,
            cost_estimate,
        )

        self.assertTrue(is_dataclass(result))
        self.assertIsNotNone(result.sheet_utilization_report)
        self.assertIsNotNone(result.offcut_report)
        self.assertIsNotNone(result.offcut_intelligence_report)
        self.assertIsNotNone(result.waste_intelligence_report)
        self.assertIsNotNone(result.nesting_intelligence_report)

        self.assertEqual(result.sheet_utilization_report.sheet_count, 2)
        self.assertEqual(result.sheet_utilization_report.total_sheet_area, 15000)
        self.assertEqual(result.sheet_utilization_report.total_used_area, 7500)
        self.assertEqual(result.sheet_utilization_report.total_remaining_area, 7500)
        self.assertEqual(result.sheet_utilization_report.utilization_rate, 0.5)
        self.assertEqual(result.sheet_utilization_report.waste_rate, 0.5)

        self.assertEqual(result.offcut_intelligence_report.recommendation, "No offcuts available for reuse")
        self.assertEqual(result.offcut_intelligence_report.warnings, [])

        self.assertEqual(result.waste_intelligence_report.waste_ratio, 0.20)
        self.assertEqual(result.waste_intelligence_report.waste_cost, 88.0)
        self.assertEqual(result.waste_intelligence_report.risk_level, "MEDIUM")
        self.assertEqual(
            result.waste_intelligence_report.recommendation,
            "Moderate waste risk: review sheet utilization",
        )
        self.assertEqual(
            result.waste_intelligence_report.warnings,
            ["Consumption warning", "Cost warning"],
        )

        self.assertEqual(result.nesting_intelligence_report.utilization_rate, 0.5)
        self.assertEqual(result.nesting_intelligence_report.waste_rate, 0.5)
        self.assertEqual(result.nesting_intelligence_report.recovery_score, 0)
        self.assertEqual(result.nesting_intelligence_report.risk_level, "MEDIUM")
        self.assertEqual(
            result.nesting_intelligence_report.recommendation,
            "Review nesting layout for better sheet utilization",
        )
        self.assertEqual(
            result.nesting_intelligence_report.warnings,
            ["Consumption warning", "Cost warning"],
        )

        self.assertEqual(self._snapshot(sheet_results), sheet_results_snapshot)
        self.assertEqual(self._snapshot(consumption_report), consumption_snapshot)
        self.assertEqual(self._snapshot(cost_estimate), cost_snapshot)

        self.assertFalse(hasattr(type(result), "build"))
        self.assertFalse(hasattr(type(result), "calculate"))
        self.assertFalse(hasattr(type(result), "compute"))
        self.assertFalse(hasattr(type(result), "manufacture"))

    @staticmethod
    def _snapshot(value):
        if isinstance(value, list):
            return [
                {
                    key: list(item_value) if isinstance(item_value, list) else item_value
                    for key, item_value in item.__dict__.items()
                }
                for item in value
            ]
        return {
            key: list(item_value) if isinstance(item_value, list) else item_value
            for key, item_value in value.__dict__.items()
        }


if __name__ == "__main__":
    unittest.main()
