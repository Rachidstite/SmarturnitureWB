import unittest

from validation.intelligence.engineering.engineering_rule_engine import (
    EngineeringRuleEngine,
)

from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class DummyRule:

    def validate(
        self,
        panel_spec,
    ):
        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="dummy",
        )


class EngineeringRuleEngineTests(
    unittest.TestCase
):

    def test_engine_executes_rules(
        self,
    ):

        panel = object()

        results = (
            EngineeringRuleEngine(
                rules=[
                    DummyRule()
                ]
            )
            .validate(
                [panel]
            )
        )

        self.assertEqual(
            1,
            len(results)
        )


if __name__ == "__main__":
    unittest.main()
