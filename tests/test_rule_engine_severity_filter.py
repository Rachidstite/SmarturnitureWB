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


class TestRuleEngineSeverityFilter(
    unittest.TestCase
):

    def test_filter_errors(self):

        engine = ManufacturingRuleEngine()

        results = [
            RuleResult(
                passed=False,
                level=ResultLevel.ERROR,
                code="E1",
                message="error"
            ),
            RuleResult(
                passed=True,
                level=ResultLevel.INFO,
                code="I1",
                message="info"
            ),
        ]

        errors = engine.errors(results)

        self.assertEqual(
            len(errors),
            1
        )

        self.assertEqual(
            errors[0].code,
            "E1"
        )


if __name__ == "__main__":
    unittest.main()
