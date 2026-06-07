import unittest
from types import SimpleNamespace

from validation.intelligence.unused_operation_rule import (
    UnusedOperationRule,
)

from validation.intelligence.result_level import (
    ResultLevel,
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class TestUnusedOperationRule(
    unittest.TestCase
):

    def test_unused_operation_generates_optimization(self):

        rule = UnusedOperationRule()

        panel = SimpleNamespace()

        operation = UnifiedManufacturingOperation(
            operation_type="DRILL",
            diameter=5,
            depth=10,
            metadata={}
        )

        result = rule.validate(
            panel,
            operation
        )

        self.assertFalse(
            result.passed
        )

        self.assertEqual(
            result.level,
            ResultLevel.OPTIMIZATION
        )

    def test_operation_with_intent_is_valid(self):

        rule = UnusedOperationRule()

        panel = SimpleNamespace()

        operation = UnifiedManufacturingOperation(
            operation_type="DRILL",
            diameter=5,
            depth=10,
            metadata={
                "hardware_intent":
                "INTENT_MINIFIX_15"
            }
        )

        result = rule.validate(
            panel,
            operation
        )

        self.assertTrue(
            result.passed
        )


if __name__ == "__main__":
    unittest.main()
