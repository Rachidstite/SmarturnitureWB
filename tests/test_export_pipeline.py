import unittest

from domain.builders import WardrobeBuilder

from exports.cutlist_engine import CutListEngine
from exports.bom_engine import BOMEngine
from exports.manufacturing_report import ManufacturingReportEngine


class TestExportPipeline(unittest.TestCase):

    def test_complete_export_pipeline(self):

        project = WardrobeBuilder(
            uid="TEST_EXPORT",
            width=800,
            height=800,
            depth=400
        ).build()

        cutlist = CutListEngine.extract(project.graph)
        bom = BOMEngine.generate(project.graph)
        report = ManufacturingReportEngine.generate(project.graph)

        self.assertGreater(len(cutlist), 0)
        self.assertGreater(len(bom.items), 0)

        self.assertIsNotNone(report)
        self.assertIsNotNone(report.lines)


if __name__ == "__main__":
    unittest.main()
