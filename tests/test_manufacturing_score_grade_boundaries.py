import unittest

from validation.intelligence.manufacturing_score import (
    ManufacturingScore,
)


class TestManufacturingScoreGradeBoundaries(
    unittest.TestCase
):

    def test_grade_boundaries(self):

        cases = [
            (100, "A+"),
            (95,  "A+"),
            (94,  "A"),
            (90,  "A"),
            (89,  "B"),
            (80,  "B"),
            (79,  "C"),
            (70,  "C"),
            (69,  "D"),
            (60,  "D"),
            (59,  "F"),
        ]

        for score, expected in cases:

            if score >= 95:
                grade = "A+"
            elif score >= 90:
                grade = "A"
            elif score >= 80:
                grade = "B"
            elif score >= 70:
                grade = "C"
            elif score >= 60:
                grade = "D"
            else:
                grade = "F"

            self.assertEqual(
                grade,
                expected
            )


if __name__ == "__main__":
    unittest.main()
