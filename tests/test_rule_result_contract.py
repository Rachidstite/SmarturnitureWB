import unittest

from validation.intelligence.rule_result import (
    RuleResult,
)


class TestRuleResultContract(
    unittest.TestCase
):

    def test_result_fields(self):

        result = RuleResult(
            passed=True,
            code="OK",
            message="valid"
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.code, "OK")


if __name__ == "__main__":
    unittest.main()
