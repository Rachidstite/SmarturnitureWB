import unittest
from types import SimpleNamespace

from validation.intelligence.confirmat_depth_rule import (
    ConfirmatDepthRule,
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class TestConfirmatDepthRule(
    unittest.TestCase
):

    def test_valid_confirmat_depth(self):

        panel = SimpleNamespace(
            thickness=18
        )

        operation = UnifiedManufacturingOperation(
            operation_type="DRILL",
            depth=15,
            metadata={
                "hardware_intent":
                "INTENT_CONFIRMAT_50"
            }
        )

        result = (
            ConfirmatDepthRule()
            .validate(
                panel,
                operation
            )
        )

        self.assertTrue(
            result.passed
        )

    def test_invalid_confirmat_depth(self):

        panel = SimpleNamespace(
            thickness=18
        )

        operation = UnifiedManufacturingOperation(
            operation_type="DRILL",
            depth=8,
            metadata={
                "hardware_intent":
                "INTENT_CONFIRMAT_50"
            }
        )

        result = (
            ConfirmatDepthRule()
            .validate(
                panel,
                operation
            )
        )

        self.assertFalse(
            result.passed
        )


if __name__ == "__main__":
    unittest.main()
