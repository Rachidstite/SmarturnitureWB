import unittest
from unittest.mock import patch


class TestProjectCostCalculator(unittest.TestCase):

    def test_project_cost_calculator_exists(self):

        try:
            from cost_intelligence.project_cost_calculator import (
                ProjectCostCalculator,
            )
        except ImportError:
            self.fail(
                "ProjectCostCalculator does not exist"
            )

    def test_project_cost_calculator_orchestrates_existing_calculators(self):

        from cost_intelligence.cost_estimate import CostEstimate
        from cost_intelligence.cost_report import CostReport
        from cost_intelligence.project_cost_calculator import (
            ProjectCostCalculator,
        )

        material_estimate = CostEstimate(
            material_cost=50,
        )
        sheet_estimate = CostEstimate(
            sheet_cost=560,
        )
        waste_estimate = CostEstimate(
            waste_cost=84,
        )
        hardware_estimate = CostEstimate(
            hardware_cost=48,
        )

        with patch(
            "cost_intelligence.project_cost_calculator.MaterialCostCalculator"
        ) as material_calculator, patch(
            "cost_intelligence.project_cost_calculator.SheetCostCalculator"
        ) as sheet_calculator, patch(
            "cost_intelligence.project_cost_calculator.WasteCostCalculator"
        ) as waste_calculator, patch(
            "cost_intelligence.project_cost_calculator.HardwareCostCalculator"
        ) as hardware_calculator:
            material_calculator.return_value.estimate.return_value = (
                material_estimate
            )
            sheet_calculator.return_value.estimate.return_value = (
                sheet_estimate
            )
            waste_calculator.return_value.estimate.return_value = (
                waste_estimate
            )
            hardware_calculator.return_value.estimate.return_value = (
                hardware_estimate
            )

            report = ProjectCostCalculator().estimate(
                cutlist_items=[],
                nesting_results={},
                hardware_items=[],
                pricing_catalog={},
            )

        material_calculator.return_value.estimate.assert_called_once()
        sheet_calculator.return_value.estimate.assert_called_once()
        waste_calculator.return_value.estimate.assert_called_once()
        hardware_calculator.return_value.estimate.assert_called_once()

        self.assertIsInstance(
            report,
            CostReport,
        )

        self.assertEqual(
            report.total_cost,
            742,
        )


if __name__ == "__main__":
    unittest.main()
