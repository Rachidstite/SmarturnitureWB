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


class TestExportDecisionPolicy(
    unittest.TestCase
):

    def test_can_export_without_errors(self):

        engine = ManufacturingRuleEngine()

        results = [
            RuleResult(
                passed=True,
                level=ResultLevel.INFO,
                code="INFO",
                message="ok"
            )
        ]

        self.assertTrue(
            engine.can_export(results)
        )

    def test_cannot_export_with_errors(self):

        engine = ManufacturingRuleEngine()

        results = [
            RuleResult(
                passed=False,
                level=ResultLevel.ERROR,
                code="ERR",
                message="fatal"
            )
        ]

        self.assertFalse(
            engine.can_export(results)
        )


if __name__ == "__main__":
    unittest.main()
