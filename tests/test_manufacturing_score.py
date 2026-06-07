import unittest

from validation.intelligence.manufacturing_score import (
    ManufacturingScore,
)


class TestManufacturingScore(
    unittest.TestCase
):

    def test_fields_exist(self):

        score = ManufacturingScore(
            score=95,
            grade="A",
            explanation="Excellent manufacturing quality",
        )

        self.assertEqual(
            score.score,
            95
        )

        self.assertEqual(
            score.grade,
            "A"
        )


if __name__ == "__main__":
    unittest.main()
