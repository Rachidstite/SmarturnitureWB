import unittest
from types import SimpleNamespace

from validation.intelligence.manufacturing_rule_engine import (
    ManufacturingRuleEngine,
)

from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)


class TestManufacturingRuleEngine(
    unittest.TestCase
):

    def test_engine_executes_rules(self):

        panel = SimpleNamespace(
            width=600,
            height=800,
            unified_operations=[
                UnifiedManufacturingOperation(
                    operation_type="DRILL",
                    x=100,
                    y=100,
                )
            ]
        )

        results = (
            ManufacturingRuleEngine()
            .validate([panel])
        )

        self.assertGreater(
            len(results),
            0
        )

        self.assertTrue(
            results[0].passed
        )


if __name__ == "__main__":
    unittest.main()
