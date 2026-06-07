import unittest

from validation.intelligence.rules_registry import (
    RulesRegistry,
)


class TestRuleRegistryArchitecture(
    unittest.TestCase
):

    def test_registry_returns_rules(self):

        rules = RulesRegistry.get_rules()

        self.assertGreater(
            len(rules),
            0
        )


if __name__ == "__main__":
    unittest.main()
