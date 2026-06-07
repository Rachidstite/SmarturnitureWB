import unittest

from validation.intelligence.cost_impact import (
    CostImpact,
)


class TestCostImpact(
    unittest.TestCase
):

    def test_fields_exist(self):

        impact = CostImpact(
            category="DRILLING",
            estimated_savings=12.5,
            description="Remove unused operation",
        )

        self.assertEqual(
            impact.category,
            "DRILLING"
        )

        self.assertEqual(
            impact.estimated_savings,
            12.5
        )


if __name__ == "__main__":
    unittest.main()
