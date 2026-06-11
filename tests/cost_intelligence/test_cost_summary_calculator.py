import unittest


class TestCostSummaryCalculator(unittest.TestCase):

    def test_cost_summary_calculator_exists(self):

        try:
            from cost_intelligence.cost_summary_calculator import (
                CostSummaryCalculator,
            )
        except ImportError:
            self.fail(
                "CostSummaryCalculator does not exist"
            )



    def test_cost_summary_calculator_combines_material_and_sheet_costs(self):

        from cost_intelligence.cost_estimate import CostEstimate
        from cost_intelligence.cost_summary_calculator import (
            CostSummaryCalculator,
        )

        material_estimate = CostEstimate(
            material_cost=50,
            total_cost=50,
        )

        sheet_estimate = CostEstimate(
            sheet_cost=560,
            total_cost=560,
        )

        result = CostSummaryCalculator().estimate(
            material_estimate=material_estimate,
            sheet_estimate=sheet_estimate,
        )

        self.assertEqual(
            result.material_cost,
            50,
        )

        self.assertEqual(
            result.sheet_cost,
            560,
        )

        self.assertEqual(
            result.total_cost,
            610,
        )


    def test_cost_summary_calculator_combines_waste_cost(self):

        from cost_intelligence.cost_estimate import CostEstimate
        from cost_intelligence.cost_summary_calculator import (
            CostSummaryCalculator,
        )

        material_estimate = CostEstimate(
            material_cost=50,
            total_cost=50,
        )

        sheet_estimate = CostEstimate(
            sheet_cost=560,
            total_cost=560,
        )

        waste_estimate = CostEstimate(
            waste_cost=84,
            total_cost=84,
        )

        result = CostSummaryCalculator().estimate(
            material_estimate=material_estimate,
            sheet_estimate=sheet_estimate,
            waste_estimate=waste_estimate,
        )

        self.assertEqual(
            result.waste_cost,
            84,
        )

        self.assertEqual(
            result.total_cost,
            694,
        )

if __name__ == "__main__":
    unittest.main()
