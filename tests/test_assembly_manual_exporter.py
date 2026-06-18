import tempfile
import unittest
from pathlib import Path

from domain.assembly_graph import JoineryGraph
from domain.builders import Identity, SceneGraph, SceneNode
from domain.core_types import MachiningOperation, NodeRole
from exports.assembly_exporter import AssemblyManualExporter


class TestAssemblyManualExporter(unittest.TestCase):

    def test_export_includes_hardware_drilling_section_from_machining_ops(self):
        graph = SceneGraph()
        side = SceneNode(
            Identity("SIDE_PANEL_1"),
            NodeRole.SIDE_PANEL,
            600.0,
            720.0,
            18.0,
            "MDF_18_WHITE",
        )
        side.machining_ops.append(
            MachiningOperation(
                op_type="DRILL",
                face="LEFT",
                local_x=32.0,
                local_y=50.0,
                diameter=3.0,
                depth=12.0,
                axis="Z",
                is_through=False,
            )
        )
        graph.add_node(side)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "assembly_manual.html"

            AssemblyManualExporter.export(graph, JoineryGraph(), str(output_path))

            html = output_path.read_text(encoding="utf-8")

        self.assertIn("Hardware Drilling / Marking", html)
        self.assertIn("S-01", html)
        self.assertIn("DRILL", html)
        self.assertIn("LEFT", html)
        self.assertIn("X=32.0", html)
        self.assertIn("Y=50.0", html)
        self.assertIn("3.0mm", html)
        self.assertIn("12.0mm", html)


if __name__ == "__main__":
    unittest.main()
