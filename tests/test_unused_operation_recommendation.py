import unittest
from types import SimpleNamespace

from validation.intelligence.unused_operation_recommendation import (
    UnusedOperationRecommendation,
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class TestUnusedOperationRecommendation(
    unittest.TestCase
):

    def test_generates_recommendation(self):

        recommendation = (
            UnusedOperationRecommendation()
        )

        panel = SimpleNamespace(
            unified_operations=[
                UnifiedManufacturingOperation(
                    operation_type="DRILL",
                    metadata={}
                )
            ]
        )

        results = recommendation.recommend(
            [panel]
        )

        self.assertEqual(
            len(results),
            1
        )


if __name__ == "__main__":
    unittest.main()
