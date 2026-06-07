import unittest

from domain.builders import WardrobeBuilder

from domain.rules_engine import (
    RuleContext,
    HardwarePlacementEngine,
)

from domain.manufacturing_compiler import (
    ManufacturingCompiler,
)

from manufacturing.hybrid_extractor import (
    HybridManufacturingExtractor,
)

from validation.intelligence.manufacturing_rule_engine import (
    ManufacturingRuleEngine,
)


class TestManufacturingIntelligencePipeline(
    unittest.TestCase
):

    def test_reference_project_passes_rules(self):

        project = (
            WardrobeBuilder(
                uid="INTELLIGENCE",
                width=1000,
                height=2000,
                depth=600,
            ).build()
        )

        context = RuleContext()

        HardwarePlacementEngine(
            context
        ).process(project)

        ManufacturingCompiler().compile(
            project,
            context
        )

        panel_specs = (
            HybridManufacturingExtractor
            .extract(project.graph)
        )

        results = (
            ManufacturingRuleEngine()
            .validate(panel_specs)
        )

        self.assertGreater(
            len(results),
            0
        )

        failures = [
            r for r in results
            if not r.passed
        ]

        self.assertEqual(
            len(failures),
            0
        )


if __name__ == "__main__":
    unittest.main()
