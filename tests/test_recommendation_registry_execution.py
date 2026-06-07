import unittest

from validation.intelligence.recommendation_registry import (
    RecommendationRegistry,
)


class TestRecommendationRegistryExecution(
    unittest.TestCase
):

    def test_registry_returns_rules(self):

        rules = (
            RecommendationRegistry
            .get_rules()
        )

        self.assertGreater(
            len(rules),
            0
        )


if __name__ == "__main__":
    unittest.main()
