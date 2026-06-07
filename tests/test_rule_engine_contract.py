import unittest

from validation.intelligence.manufacturing_rule_engine import (
    ManufacturingRuleEngine,
)


class TestRuleEngineContract(
    unittest.TestCase
):

    def test_engine_has_validate_method(self):

        self.assertTrue(
            hasattr(
                ManufacturingRuleEngine,
                "validate"
            )
        )


if __name__ == "__main__":
    unittest.main()
