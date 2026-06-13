import unittest


class TestCostEstimateContract(unittest.TestCase):

    def test_cost_estimate_contract_exists(self):

        try:
            from cost_intelligence.cost_estimate import (
                CostEstimate,
            )
        except ImportError:
            self.fail(
                "CostEstimate does not exist"
            )

    def test_cost_estimate_has_required_fields(self):

        from cost_intelligence.cost_estimate import (
            CostEstimate,
        )

        estimate = CostEstimate()

        self.assertTrue(
            hasattr(
                estimate,
                "material_cost",
            )
        )

        self.assertTrue(
            hasattr(
                estimate,
                "sheet_cost",
            )
        )

        self.assertTrue(
            hasattr(
                estimate,
                "waste_cost",
            )
        )

        self.assertTrue(
            hasattr(
                estimate,
                "total_cost",
            )
        )

        self.assertTrue(
            hasattr(
                estimate,
                "currency",
            )
        )


if __name__ == "__main__":
    unittest.main()
