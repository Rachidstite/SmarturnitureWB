import unittest

from validation.intelligence.engineering.engineering_assembly_rule_engine import (
    EngineeringAssemblyRuleEngine,
)

from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class DummyAssemblyRule:

    def validate(
        self,
        scene_graph,
    ):
        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="assembly",
        )


class AssemblyEngineTests(
    unittest.TestCase
):

    def test_engine_executes_rules(
        self,
    ):

        results = (
            EngineeringAssemblyRuleEngine(
                rules=[
                    DummyAssemblyRule()
                ]
            )
            .validate(
                object()
            )
        )

        self.assertEqual(
            1,
            len(results)
        )


if __name__ == "__main__":
    unittest.main()
