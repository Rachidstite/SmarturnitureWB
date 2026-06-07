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


class TestRuleEngineSummary(
    unittest.TestCase
):

    def test_summary_counts(self):

        engine = ManufacturingRuleEngine()

        results = [
            RuleResult(
                passed=False,
                level=ResultLevel.ERROR,
                code="E",
                message="error"
            ),
            RuleResult(
                passed=True,
                level=ResultLevel.WARNING,
                code="W",
                message="warning"
            ),
            RuleResult(
                passed=True,
                level=ResultLevel.INFO,
                code="I",
                message="info"
            ),
        ]

        summary = engine.summary(results)

        self.assertEqual(summary["errors"], 1)
        self.assertEqual(summary["warnings"], 1)
        self.assertEqual(summary["infos"], 1)


if __name__ == "__main__":
    unittest.main()
