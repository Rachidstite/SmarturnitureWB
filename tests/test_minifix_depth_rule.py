import unittest
from types import SimpleNamespace

from validation.intelligence.minifix_depth_rule import (
    MinifixDepthRule,
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class TestMinifixDepthRule(
    unittest.TestCase
):

    def test_valid_minifix_depth(self):

        panel = SimpleNamespace(
            thickness=18
        )

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            diameter=15,
            depth=14,
            metadata={
                "hardware_intent":
                "INTENT_MINIFIX_15"
            }
        )

        result = (
            MinifixDepthRule()
            .validate(panel, op)
        )

        self.assertTrue(result.passed)

    def test_depth_too_small(self):

        panel = SimpleNamespace(
            thickness=18
        )

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            diameter=15,
            depth=10,
            metadata={
                "hardware_intent":
                "INTENT_MINIFIX_15"
            }
        )

        result = (
            MinifixDepthRule()
            .validate(panel, op)
        )

        self.assertFalse(result.passed)
        self.assertEqual(
            result.code,
            "MINIFIX_DEPTH"
        )


if __name__ == "__main__":
    unittest.main()
