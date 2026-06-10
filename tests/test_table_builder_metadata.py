import unittest

from runtime.table_builder import TableBuilder


class TestTableBuilderMetadata(unittest.TestCase):

    def test_table_nodes_have_furniture_type_metadata(self):

        project = TableBuilder(
            uid="TABLE_META",
        ).build()

        furniture_types = {
            node.metadata.get("furniture_type")
            for node in project.graph.physical_nodes
        }

        self.assertEqual(
            furniture_types,
            {"TABLE"},
        )


if __name__ == "__main__":
    unittest.main()
