import unittest

from runtime.table_builder import TableBuilder
from domain.rules_engine import RuleContext, HardwarePlacementEngine
from domain.manufacturing_compiler import ManufacturingCompiler


class TestTableBuilderManufacturingCompile(unittest.TestCase):

    def test_table_project_enters_manufacturing_compiler(self):

        project = TableBuilder(
            uid="TABLE_MFG",
            width=1200,
            depth=700,
            height=750,
        ).build()

        context = RuleContext()

        HardwarePlacementEngine(
            context
        ).process(project)

        ManufacturingCompiler().compile(
            project,
            context,
        )

        self.assertIsNotNone(project.graph)
        self.assertGreaterEqual(
            len(project.graph.physical_nodes),
            5,
        )


if __name__ == "__main__":
    unittest.main()
