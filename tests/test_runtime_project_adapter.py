import unittest

from scene_graph.scene_graph import SceneGraph

from runtime.runtime_project_adapter import (
    RuntimeProjectAdapter,
)


class TestRuntimeProjectAdapter(
    unittest.TestCase
):

    def test_creates_cabinet_project(self):

        graph = SceneGraph()

        project = (
            RuntimeProjectAdapter
            .from_scene_graph(graph)
        )

        self.assertIs(
            project.graph,
            graph,
        )

        self.assertEqual(
            len(project.placements),
            0,
        )

    def test_creates_joinery_graph(self):

        graph = SceneGraph()

        project = (
            RuntimeProjectAdapter
            .from_scene_graph(graph)
        )

        self.assertIsNotNone(
            project.joinery,
        )

        self.assertTrue(
            hasattr(
                project.joinery,
                "edges",
            )
        )


if __name__ == "__main__":
    unittest.main()
