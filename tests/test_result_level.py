import unittest

from validation.intelligence.result_level import (
    ResultLevel,
)


class TestResultLevel(
    unittest.TestCase
):

    def test_levels_exist(self):

        self.assertEqual(
            ResultLevel.ERROR.value,
            "ERROR"
        )

        self.assertEqual(
            ResultLevel.WARNING.value,
            "WARNING"
        )

        self.assertEqual(
            ResultLevel.RECOMMENDATION.value,
            "RECOMMENDATION"
        )

        self.assertEqual(
            ResultLevel.OPTIMIZATION.value,
            "OPTIMIZATION"
        )

        self.assertEqual(
            ResultLevel.INFO.value,
            "INFO"
        )


if __name__ == "__main__":
    unittest.main()
