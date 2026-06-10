import unittest

from runtime.table_builder import TableBuilder
from exports.cutlist_engine import CutListEngine
from exports.nesting_engine import IndustrialNestingEngine
from exports.strategies import GuillotineStripStrategy


class TestTableBuilderNestingE2E(unittest.TestCase):

    def test_table_cutlist_generates_nesting_sheet(self):

        project = TableBuilder(
            uid="TABLE_NESTING_E2E",
        ).build()

        cutlist = CutListEngine.extract(
            project.graph
        )

        result = IndustrialNestingEngine(
            GuillotineStripStrategy()
        ).process(cutlist)

        self.assertIn(
            "MDF_18MM",
            result,
        )

        self.assertGreaterEqual(
            len(result["MDF_18MM"]),
            1,
        )


if __name__ == "__main__":
    unittest.main()
