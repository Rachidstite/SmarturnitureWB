import unittest

from validation.intelligence.recommendation_engine import (
    RecommendationEngine,
)


class TestRecommendationEngineContract(
    unittest.TestCase
):

    def test_engine_has_recommend_method(self):

        self.assertTrue(
            hasattr(
                RecommendationEngine,
                "recommend"
            )
        )


if __name__ == "__main__":
    unittest.main()
