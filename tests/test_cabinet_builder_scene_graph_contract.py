import unittest


class TestCabinetBuilderSceneGraphContract(
    unittest.TestCase
):

    def test_builder_declares_scene_graph_attribute(self):

        with open(
            "engine/cabinet_builder.py",
            "r",
            encoding="utf-8",
        ) as f:
            source = f.read()

        self.assertIn(
            "self.scene_graph",
            source,
        )


if __name__ == "__main__":
    unittest.main()
