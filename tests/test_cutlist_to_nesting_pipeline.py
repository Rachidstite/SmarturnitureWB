import unittest

from runtime.table_builder import TableBuilder
from exports.cutlist_engine import CutListEngine
from exports.nesting_engine import IndustrialNestingEngine
from exports.strategies import GuillotineStripStrategy


class TestCutListToNestingPipeline(unittest.TestCase):

    def test_table_cutlist_can_enter_nesting_engine(self):

        project = TableBuilder(
            uid="TABLE_NESTING",
        ).build()

        cutlist = CutListEngine.extract(
            project.graph
        )

        engine = IndustrialNestingEngine(
            GuillotineStripStrategy()
        )

        result = engine.process(
            cutlist
        )

        self.assertIsNotNone(
            result
        )


if __name__ == "__main__":
    unittest.main()
