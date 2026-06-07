import unittest


class TestDashboardRequiresSceneGraph(
    unittest.TestCase
):

    def test_legacy_builder_had_scene_graph_support(self):

        with open(
            "engine/cabinet_builder.py.pre_divider_migration",
            "r",
            encoding="utf-8",
        ) as f:
            source = f.read()

        self.assertIn(
            "self.scene_graph",
            source,
        )

        self.assertIn(
            "SceneGraphBuilder",
            source,
        )


if __name__ == "__main__":
    unittest.main()
