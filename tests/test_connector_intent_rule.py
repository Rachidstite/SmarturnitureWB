import unittest
from types import SimpleNamespace

from validation.intelligence.connector_intent_rule import (
    ConnectorIntentRule,
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class TestConnectorIntentRule(
    unittest.TestCase
):

    def test_valid_intent(self):

        rule = ConnectorIntentRule()

        panel = SimpleNamespace()

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            metadata={
                "hardware_intent":
                "INTENT_MINIFIX_15"
            }
        )

        result = rule.validate(
            panel,
            op
        )

        self.assertTrue(
            result.passed
        )

    def test_invalid_intent(self):

        rule = ConnectorIntentRule()

        panel = SimpleNamespace()

        op = UnifiedManufacturingOperation(
            operation_type="DRILL",
            metadata={
                "hardware_intent":
                "INTENT_UNKNOWN"
            }
        )

        result = rule.validate(
            panel,
            op
        )

        self.assertFalse(
            result.passed
        )

        self.assertEqual(
            result.code,
            "UNKNOWN_INTENT"
        )


if __name__ == "__main__":
    unittest.main()
