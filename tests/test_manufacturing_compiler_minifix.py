import unittest


class TestManufacturingCompilerMinifix(unittest.TestCase):

    def test_minifix_hardware_placement_and_compiler_generate_machining_ops(self):
        from domain.builders import WardrobeBuilder
        from domain.core_types import JoineryType
        from domain.rules_engine import HardwarePlacementEngine, RuleContext
        from domain.manufacturing_compiler import ManufacturingCompiler

        project = WardrobeBuilder(
            uid="MINIFIX_COVERAGE",
            width=1000,
            height=2000,
            depth=600,
        ).build()

        context = RuleContext(preferred_connector=JoineryType.MINIFIX_15)

        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        self.assertGreater(len(project.placements), 0)
        self.assertTrue(
            all(
                placement.hardware_intent == "INTENT_MINIFIX_15"
                for placement in project.placements
                if placement.hardware_intent == "INTENT_MINIFIX_15"
            )
        )
        self.assertEqual(
            context.hardware_profile["INTENT_MINIFIX_15"],
            "MINIFIX_15_V1",
        )

        all_ops = []
        for node in project.graph.physical_nodes:
            all_ops.extend(getattr(node, "machining_ops", []))

        self.assertTrue(any(op.diameter == 15 for op in all_ops))
        self.assertTrue(any(op.diameter == 8 for op in all_ops))
        self.assertTrue(
            any(
                getattr(op, "op_type", "") == "DRILL"
                for op in all_ops
            )
        )


if __name__ == "__main__":
    unittest.main()
