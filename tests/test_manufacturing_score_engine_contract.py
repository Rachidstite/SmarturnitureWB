import unittest

from validation.intelligence.manufacturing_score_engine import (
    ManufacturingScoreEngine,
)


class TestManufacturingScoreEngineContract(
    unittest.TestCase
):

    def test_engine_has_calculate_method(self):

        self.assertTrue(
            hasattr(
                ManufacturingScoreEngine,
                "calculate"
            )
        )


if __name__ == "__main__":
    unittest.main()
