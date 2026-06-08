import unittest

from scene_graph.scene_graph import SceneGraph

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


if __name__ == "__main__":
    unittest.main()
