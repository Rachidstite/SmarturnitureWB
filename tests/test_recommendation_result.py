import unittest

from validation.intelligence.recommended_result import (
    RecommendationResult,
)


class TestRecommendationResult(
    unittest.TestCase
):

    def test_fields_exist(self):

        result = RecommendationResult(
            category="SAVINGS",
            title="Reduce drilling",
            message="Can reduce operations",
        )

        self.assertEqual(
            result.category,
            "SAVINGS"
        )


if __name__ == "__main__":
    unittest.main()
