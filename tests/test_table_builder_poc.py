import unittest

from runtime.table_builder import TableBuilder


class TestTableBuilderPOC(unittest.TestCase):

    def test_builds_table_project(self):

        project = TableBuilder(
            uid="TABLE_TEST",
            width=1200,
            depth=700,
            height=750,
        ).build()

        self.assertIsNotNone(project)
        self.assertIsNotNone(project.graph)
        self.assertEqual(len(project.graph.physical_nodes), 5)
        self.assertIsNotNone(project.joinery)


if __name__ == "__main__":
    unittest.main()
