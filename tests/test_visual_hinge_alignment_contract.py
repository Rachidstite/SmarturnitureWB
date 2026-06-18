import unittest

from domain.builders import Identity, SceneGraph, SceneNode
from domain.core_types import NodeRole
from domain.rules_engine import HingeRule, RuleContext
from domain.system32 import System32Engine


class TestVisualHingeAlignmentContract(unittest.TestCase):

    DRIFT_CASES = {
        600.0: [0.0, 0.0],
        1000.0: [0.0, 0.0, 0.0],
        1800.0: [0.0, -39.33333333333337, 21.333333333333258, 0.0],
        2200.0: [0.0, -40.66666666666663, 18.666666666666742, 0.0],
    }

    def test_current_visual_and_manufacturing_hinge_offsets_match_short_doors(self):
        for height in (600.0, 1000.0):
            with self.subTest(height=height):
                visual_offsets = System32Engine.hinge_positions(height)
                manufacturing_offsets = self._hinge_rule_offsets(height)

                self.assertEqual(visual_offsets, manufacturing_offsets)

    def test_current_visual_and_manufacturing_hinge_offsets_document_tall_door_drift(self):
        for height in (1800.0, 2200.0):
            with self.subTest(height=height):
                visual_offsets = System32Engine.hinge_positions(height)
                manufacturing_offsets = self._hinge_rule_offsets(height)
                drift = [
                    visual - manufacturing
                    for visual, manufacturing in zip(
                        visual_offsets,
                        manufacturing_offsets,
                    )
                ]

                self.assertEqual(len(visual_offsets), len(manufacturing_offsets))
                self.assertNotEqual(visual_offsets, manufacturing_offsets)
                self.assert_offsets_close(drift, self.DRIFT_CASES[height])

    @unittest.expectedFailure
    def test_future_visual_hinge_offsets_should_equal_hinge_rule_offsets(self):
        for height in (600.0, 1000.0, 1800.0, 2200.0):
            with self.subTest(height=height):
                visual_offsets = System32Engine.hinge_positions(height)
                manufacturing_offsets = self._hinge_rule_offsets(height)

                self.assertEqual(visual_offsets, manufacturing_offsets)

    @staticmethod
    def _hinge_rule_offsets(height):
        graph = SceneGraph()
        door = SceneNode(
            Identity(f"VISUAL_HINGE_ALIGNMENT_DOOR_{int(height)}"),
            NodeRole.DOOR_PANEL,
            500.0,
            height,
            18.0,
            "MDF_18_WHITE",
        )
        graph.add_node(door)
        project = type(
            "VisualHingeAlignmentProject",
            (),
            {
                "graph": graph,
                "joinery": type("EmptyJoinery", (), {"edges": []})(),
                "placements": [],
            },
        )()

        return [
            placement.anchor.offset_y
            for placement in HingeRule().apply(project, RuleContext())
        ]

    def assert_offsets_close(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for actual_offset, expected_offset in zip(actual, expected):
            self.assertAlmostEqual(actual_offset, expected_offset, places=6)


if __name__ == "__main__":
    unittest.main()
