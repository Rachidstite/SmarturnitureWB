import unittest

from domain.hardware_recommendation_engine import (
    HardwareRecommendationEngine,
)


class TestHardwareRecommendationEngine(unittest.TestCase):

    def test_small_shelf_recommends_confirmat(self):
        result = HardwareRecommendationEngine().recommend(
            role="SHELF",
            span=500,
            thickness=18,
        )

        self.assertEqual(
            result.hardware_id,
            "CONFIRMAT_50_V1",
        )

        self.assertEqual(
            result.confidence,
            "HIGH",
        )

    def test_medium_shelf_recommends_minifix(self):
        result = HardwareRecommendationEngine().recommend(
            role="SHELF",
            span=800,
            thickness=18,
        )

        self.assertEqual(
            result.hardware_id,
            "MINIFIX_15_V1",
        )

        self.assertEqual(
            result.confidence,
            "HIGH",
        )

    def test_large_shelf_recommends_minifix(self):
        result = HardwareRecommendationEngine().recommend(
            role="SHELF",
            span=1200,
            thickness=18,
        )

        self.assertEqual(
            result.hardware_id,
            "MINIFIX_15_V1",
        )

        self.assertEqual(
            result.confidence,
            "MEDIUM",
        )

        self.assertIn(
            "Large span",
            result.reason,
        )

    def test_unknown_role_returns_none(self):
        result = HardwareRecommendationEngine().recommend(
            role="UNKNOWN",
            span=800,
            thickness=18,
        )

        self.assertIsNone(result)

    def test_recommendation_is_immutable(self):
        result = HardwareRecommendationEngine().recommend(
            role="SHELF",
            span=500,
            thickness=18,
        )

        with self.assertRaises(Exception):
            result.hardware_id = "TEST"


if __name__ == "__main__":
    unittest.main()
