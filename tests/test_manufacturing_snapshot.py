import unittest

from domain.builders import WardrobeBuilder
from exports.cutlist_engine import CutListEngine
from exports.bom_engine import BOMEngine
from exports.manufacturing_report import ManufacturingReportEngine
from manufacturing.panel_operation_engine import PanelOperationEngine
from assembly.assembly_graph_builder import AssemblyGraphBuilder


class TestManufacturingSnapshot(unittest.TestCase):

    def test_reference_wardrobe_snapshot(self):

        project = WardrobeBuilder(
            uid="SNAPSHOT",
            width=800,
            height=800,
            depth=400
        ).build()

        assembly = AssemblyGraphBuilder.build(
            project.graph
        )

        panel_ops = PanelOperationEngine.generate(
            project.graph
        )

        cutlist = CutListEngine.extract(
            project.graph
        )

        bom = BOMEngine.generate(
            project.graph
        )

        report = ManufacturingReportEngine.generate(
            project.graph
        )

        self.assertEqual(
            len(assembly.all_joints()),
            4,
            "Manufacturing regression: joint count changed"
        )

        self.assertEqual(
            len(panel_ops),
            2,
            "Manufacturing regression: panels with operations changed"
        )

        self.assertEqual(
            sum(len(v) for v in panel_ops.values()),
            8,
            "Manufacturing regression: operation count changed"
        )

        self.assertEqual(
            len(cutlist),
            5,
            "Manufacturing regression: cutlist changed"
        )

        self.assertEqual(
            len(bom.items),
            5,
            "Manufacturing regression: BOM changed"
        )

        self.assertEqual(
            len(report.lines),
            8,
            "Manufacturing regression: report changed"
        )


if __name__ == "__main__":
    unittest.main()
