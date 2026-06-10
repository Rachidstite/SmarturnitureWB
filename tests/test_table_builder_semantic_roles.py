import unittest

from runtime.table_builder import TableBuilder


class TestTableBuilderSemanticRoles(unittest.TestCase):

    def test_table_nodes_have_semantic_roles(self):

        project = TableBuilder(
            uid="TABLE_SEMANTIC",
        ).build()

        semantic_roles = {
            node.metadata.get("semantic_role")
            for node in project.graph.physical_nodes
        }

        self.assertEqual(
            semantic_roles,
            {"TABLE_TOP", "TABLE_LEG"},
        )


if __name__ == "__main__":
    unittest.main()
