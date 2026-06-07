import unittest

from validation.intelligence.rule_result import (
    RuleResult,
)

from validation.intelligence.result_level import (
    ResultLevel,
)


class TestRuleResultLevel(
    unittest.TestCase
):

    def test_level_is_stored(self):

        result = RuleResult(
            passed=True,
            level=ResultLevel.INFO,
            code="OK",
            message="valid"
        )

        self.assertEqual(
            result.level,
            ResultLevel.INFO
        )


if __name__ == "__main__":
    unittest.main()
