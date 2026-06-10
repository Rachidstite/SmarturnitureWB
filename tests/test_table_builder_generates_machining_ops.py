import unittest

from runtime.table_builder import TableBuilder
from domain.rules_engine import RuleContext, HardwarePlacementEngine
from domain.manufacturing_compiler import ManufacturingCompiler


class TestTableBuilderGeneratesMachiningOps(unittest.TestCase):

    def test_table_generates_machining_operations(self):

        project = TableBuilder(
            uid="TABLE_OPS",
        ).build()

        context = RuleContext()

        HardwarePlacementEngine(
            context
        ).process(project)

        ManufacturingCompiler().compile(
            project,
            context,
        )

        ops_counts = [
            len(getattr(node, "machining_ops", []))
            for node in project.graph.physical_nodes
        ]

        self.assertGreater(
            sum(ops_counts),
            0,
        )


if __name__ == "__main__":
    unittest.main()
