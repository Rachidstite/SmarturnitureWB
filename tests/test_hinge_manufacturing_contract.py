import unittest

from domain.builders import Identity, SceneGraph, SceneNode
from domain.core_types import NodeCategory, NodeRole
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.rules_engine import HingeRule, RuleContext


class TestHingeManufacturingContract(unittest.TestCase):

    CASES = (
        (600.0, 2, [100.0, 500.0]),
        (1000.0, 3, [100.0, 500.0, 900.0]),
        (1800.0, 4, [100.0, 633.3333333333334, 1166.6666666666667, 1700.0]),
        (2200.0, 4, [100.0, 766.6666666666666, 1433.3333333333333, 2100.0]),
    )

    def test_hinge_rule_documents_current_canonical_positions(self):
        for height, expected_count, expected_offsets in self.CASES:
            with self.subTest(height=height):
                graph, door = self._graph_with_door(height)
                project = self._project(graph)

                placements = HingeRule().apply(project, RuleContext())
                offsets = [placement.anchor.offset_y for placement in placements]

                self.assertEqual(len(placements), expected_count)
                self.assert_offsets_close(offsets, expected_offsets)
                self.assertAlmostEqual(offsets[0], 100.0)
                self.assertAlmostEqual(height - offsets[-1], 100.0)
                self.assert_even_intermediate_spacing(offsets)
                self.assertTrue(all(placement.host_node_id == door.identity.key for placement in placements))
                self.assertTrue(all(placement.target_node_id == door.identity.key for placement in placements))

    def test_hinge_placements_compile_to_physical_door_machining_operations(self):
        for height, expected_count, _expected_offsets in self.CASES:
            with self.subTest(height=height):
                graph, door = self._graph_with_door(height)
                project = self._project(graph)
                context = RuleContext()

                project.placements.extend(HingeRule().apply(project, context))
                ManufacturingCompiler().compile(project, context)

                self.assertEqual(door.category, NodeCategory.PHYSICAL)

                cup_ops = [
                    op
                    for op in door.machining_ops
                    if op.op_type == "DRILL"
                    and abs(op.diameter - 35.0) < 0.1
                    and abs(op.depth - 12.5) < 0.1
                    and op.face == "BACK"
                ]
                pilot_ops = [
                    op
                    for op in door.machining_ops
                    if op.op_type == "DRILL"
                    and abs(op.diameter - 2.5) < 0.1
                    and abs(op.depth - 10.0) < 0.1
                    and op.face == "BACK"
                ]

                self.assertEqual(len(cup_ops), expected_count)
                self.assertEqual(len(pilot_ops), expected_count * 2)
                self.assertFalse(
                    [
                        op
                        for node in graph._by_category[NodeCategory.VIRTUAL]
                        for op in getattr(node, "machining_ops", [])
                        if op.op_type == "DRILL"
                    ],
                    "Hinge machining operations must not be attached to virtual nodes",
                )

    @staticmethod
    def _graph_with_door(height):
        graph = SceneGraph()
        door = SceneNode(
            Identity(f"HINGE_CONTRACT_DOOR_{int(height)}"),
            NodeRole.DOOR_PANEL,
            500.0,
            height,
            18.0,
            "MDF_18_WHITE",
        )
        graph.add_node(door)
        return graph, door

    @staticmethod
    def _project(graph):
        return type(
            "HingeContractProject",
            (),
            {
                "graph": graph,
                "joinery": type("EmptyJoinery", (), {"edges": []})(),
                "placements": [],
            },
        )()

    def assert_offsets_close(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for actual_offset, expected_offset in zip(actual, expected):
            self.assertAlmostEqual(actual_offset, expected_offset, places=6)

    def assert_even_intermediate_spacing(self, offsets):
        if len(offsets) < 3:
            return

        spacings = [
            offsets[index + 1] - offsets[index]
            for index in range(len(offsets) - 1)
        ]
        for spacing in spacings[1:]:
            self.assertAlmostEqual(spacing, spacings[0], places=6)


if __name__ == "__main__":
    unittest.main()
