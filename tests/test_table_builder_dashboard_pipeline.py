import unittest

from runtime.table_builder import TableBuilder
from services.manufacturing_dashboard_service import (
    ManufacturingDashboardService,
)


class TestTableBuilderDashboardPipeline(unittest.TestCase):

    def test_table_scene_graph_enters_dashboard_pipeline(self):

        project = TableBuilder(
            uid="TABLE_DASHBOARD",
            width=1200,
            depth=700,
            height=750,
        ).build()

        result = ManufacturingDashboardService.build(
            project.graph
        )

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.report)
        self.assertIsNotNone(result.viewmodel)


if __name__ == "__main__":
    unittest.main()
