import unittest


class TestHingePlacementTargetCoverage(unittest.TestCase):

    def test_hinge_placements_include_target_node_id(self):
        from domain.builders import WardrobeBuilder
        from domain.rules_engine import HardwarePlacementEngine, RuleContext

        cabinet = WardrobeBuilder(
            uid="HINGE_TARGET_COVERAGE",
            width=1000,
            height=2000,
            depth=600,
        )
        cabinet.add_doors(2)
        project = cabinet.build()

        context = RuleContext()
        HardwarePlacementEngine(context).process(project)

        hinge_placements = [
            placement
            for placement in project.placements
            if placement.hardware_intent == "INTENT_HINGE"
        ]

        self.assertGreater(len(hinge_placements), 0)
        for placement in hinge_placements:
            self.assertTrue(placement.host_node_id)
            self.assertTrue(placement.target_node_id)


if __name__ == "__main__":
    unittest.main()
