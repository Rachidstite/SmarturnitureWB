import unittest

from validation.intelligence.manufacturing_rule import (
    ManufacturingRule,
)


class TestManufacturingRuleContract(
    unittest.TestCase
):

    def test_rule_has_validate_method(self):

        self.assertTrue(
            hasattr(
                ManufacturingRule,
                "validate"
            )
        )


if __name__ == "__main__":
    unittest.main()
