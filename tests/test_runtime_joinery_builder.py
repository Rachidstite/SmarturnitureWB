import unittest

from scene_graph.scene_graph import SceneGraph
from scene_graph.node import SceneNode
from shared.identity import PanelIdentity, SemanticRole
from shared.roles import NodeRole

from runtime.runtime_joinery_builder import (
    RuntimeJoineryBuilder,
)


class TestRuntimeJoineryBuilder(
    unittest.TestCase
):

    def test_returns_joinery_graph(self):

        graph = SceneGraph()

        joinery = (
            RuntimeJoineryBuilder.build(
                graph
            )
        )

        self.assertIsNotNone(
            joinery
        )

        self.assertTrue(
            hasattr(
                joinery,
                "edges",
            )
        )

    def test_builds_basic_carcass_joinery(self):

        graph = SceneGraph()

        side = SceneNode(
            identity=PanelIdentity(
                "TEST",
                "STRUCTURE",
                SemanticRole.LEFT_SIDE,
                0,
            ),
            role=NodeRole.SIDE_PANEL,
            width=600,
            height=720,
            depth=500,
            thickness=18,
            material="MDF",
            x=0,
            y=0,
            z=0,
        )

        top = SceneNode(
            identity=PanelIdentity(
                "TEST",
                "STRUCTURE",
                SemanticRole.TOP,
                0,
            ),
            role=NodeRole.TOP_PANEL,
            width=600,
            height=18,
            depth=500,
            thickness=18,
            material="MDF",
            x=0,
            y=0,
            z=720,
        )

        bottom = SceneNode(
            identity=PanelIdentity(
                "TEST",
                "STRUCTURE",
                SemanticRole.BOTTOM,
                0,
            ),
            role=NodeRole.BOTTOM_PANEL,
            width=600,
            height=18,
            depth=500,
            thickness=18,
            material="MDF",
            x=0,
            y=0,
            z=720,
        )

        graph.add_node(side)
        graph.add_node(top)
        graph.add_node(bottom)

        joinery = RuntimeJoineryBuilder.build(
            graph
        )

        self.assertGreaterEqual(
            len(joinery.edges),
            2,
        )


if __name__ == "__main__":
    unittest.main()
