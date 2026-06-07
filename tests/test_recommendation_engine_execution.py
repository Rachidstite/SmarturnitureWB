import unittest
from unittest.mock import patch

from validation.intelligence.recommendation_engine import (
    RecommendationEngine,
)


class TestRecommendationEngineExecution(
    unittest.TestCase
):

    @patch(
        "validation.intelligence.recommendation_registry.RecommendationRegistry.get_rules"
    )
    def test_engine_executes_recommendations(
        self,
        get_rules
    ):

        class FakeRule:

            def recommend(
                self,
                panel_specs
            ):
                return ["recommendation"]

        get_rules.return_value = [
            FakeRule()
        ]

        results = (
            RecommendationEngine()
            .recommend([])
        )

        self.assertEqual(
            len(results),
            1
        )


if __name__ == "__main__":
    unittest.main()
