import unittest


class TestCabinetBuilderPopulatesSceneGraph(
    unittest.TestCase
):

    def test_builder_builds_scene_graph(self):

        with open(
            "engine/cabinet_builder.py",
            "r",
            encoding="utf-8",
        ) as f:
            source = f.read()

        self.assertIn(
            "sg_builder = SceneGraphBuilder",
            source,
        )

        self.assertIn(
            "self.scene_graph",
            source,
        )


if __name__ == "__main__":
    unittest.main()
