import unittest

from validation.intelligence.rule_result import (
    RuleResult,
)

from validation.intelligence.result_level import (
    ResultLevel,
)

from validation.intelligence.manufacturing_rule_engine import (
    ManufacturingRuleEngine,
)


class TestExportBlockingPolicy(
    unittest.TestCase
):

    def test_errors_block_export(self):

        engine = ManufacturingRuleEngine()

        results = [
            RuleResult(
                passed=False,
                level=ResultLevel.ERROR,
                code="ERR",
                message="fatal"
            )
        ]

        self.assertTrue(
            engine.has_blocking_errors(results)
        )


if __name__ == "__main__":
    unittest.main()
