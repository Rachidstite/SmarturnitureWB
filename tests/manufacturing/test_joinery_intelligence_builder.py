import unittest


class TestJoineryIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.joinery_intelligence_builder import (
            JoineryIntelligenceBuilder,
        )

        self.builder = JoineryIntelligenceBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_counts_joinery_from_project(self):
        from domain.builders import WardrobeBuilder
        from domain.rules_engine import HardwarePlacementEngine, RuleContext
        from domain.manufacturing_compiler import ManufacturingCompiler

        cabinet = WardrobeBuilder(
            uid="JOINERY_INTEL",
            width=1000,
            height=2000,
            depth=600,
        )
        cabinet.add_doors(2)
        project = cabinet.build()

        context = RuleContext()
        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        report = self.builder.build(project)

        self.assertGreater(report.total_minifix, 0)
        self.assertGreater(report.total_hinges, 0)
        self.assertEqual(report.total_drawer_slides, 0)
        self.assertGreater(report.total_handles, 0)
        self.assertGreater(report.total_face_holes, 0)
        self.assertGreater(report.total_edge_holes, 0)
        self.assertGreater(report.total_cam_holes, 0)
        self.assertEqual(
            report.joinery_complexity_score,
            report.total_minifix
            + report.total_hinges
            + report.total_drawer_slides
            + report.total_handles
            + report.total_face_holes
            + report.total_edge_holes,
        )

    def test_builder_does_not_mutate_project(self):
        from domain.builders import WardrobeBuilder
        from domain.rules_engine import HardwarePlacementEngine, RuleContext
        from domain.manufacturing_compiler import ManufacturingCompiler

        cabinet = WardrobeBuilder(
            uid="JOINERY_INTEL_MUTATION",
            width=1000,
            height=2000,
            depth=600,
        )
        cabinet.add_doors(2)
        project = cabinet.build()

        context = RuleContext()
        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        placements_snapshot = [
            dict(placement.__dict__)
            for placement in project.placements
        ]
        ops_snapshot = [
            [dict(op.__dict__) for op in getattr(node, "machining_ops", [])]
            for node in project.graph.physical_nodes
        ]

        self.builder.build(project)

        self.assertEqual(
            [dict(placement.__dict__) for placement in project.placements],
            placements_snapshot,
        )
        self.assertEqual(
            [
                [dict(op.__dict__) for op in getattr(node, "machining_ops", [])]
                for node in project.graph.physical_nodes
            ],
            ops_snapshot,
        )


if __name__ == "__main__":
    unittest.main()
