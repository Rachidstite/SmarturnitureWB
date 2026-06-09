import unittest

from validation.intelligence.hardware_recommendation_rule import (
    HardwareRecommendationRule,
)


class ShelfPanel:

    role = "SHELF"
    width = 800
    thickness = 18


class UnknownPanel:

    role = "UNKNOWN"
    width = 800
    thickness = 18


class TestHardwareRecommendationRule(
    unittest.TestCase
):

    def test_generates_hardware_recommendation(self):

        results = (
            HardwareRecommendationRule()
            .recommend(
                [ShelfPanel()]
            )
        )

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0].category,
            "HARDWARE",
        )

    def test_unknown_role_generates_no_recommendation(self):

        results = (
            HardwareRecommendationRule()
            .recommend(
                [UnknownPanel()]
            )
        )

        self.assertEqual(
            results,
            [],
        )


if __name__ == "__main__":
    unittest.main()
