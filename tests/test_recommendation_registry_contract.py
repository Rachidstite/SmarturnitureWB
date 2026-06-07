import unittest

from validation.intelligence.recommendation_registry import (
    RecommendationRegistry,
)


class TestRecommendationRegistryContract(
    unittest.TestCase
):

    def test_registry_has_get_rules(self):

        self.assertTrue(
            hasattr(
                RecommendationRegistry,
                "get_rules"
            )
        )


if __name__ == "__main__":
    unittest.main()
