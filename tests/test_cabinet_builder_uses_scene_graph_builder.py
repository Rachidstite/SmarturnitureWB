import unittest


class TestCabinetBuilderUsesSceneGraphBuilder(
    unittest.TestCase
):

    def test_builder_imports_scene_graph_builder(self):

        with open(
            "engine/cabinet_builder.py",
            "r",
            encoding="utf-8",
        ) as f:
            source = f.read()

        self.assertIn(
            "from scene_graph.builder import SceneGraphBuilder",
            source,
        )


if __name__ == "__main__":
    unittest.main()
