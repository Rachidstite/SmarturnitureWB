import unittest

from validation.intelligence.recommendation_rule import (
    RecommendationRule,
)


class TestRecommendationRuleContract(
    unittest.TestCase
):

    def test_rule_has_recommend_method(self):

        self.assertTrue(
            hasattr(
                RecommendationRule,
                "recommend"
            )
        )


if __name__ == "__main__":
    unittest.main()
