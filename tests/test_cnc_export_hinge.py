import csv
import os
import tempfile
import unittest


class TestCNCExportHinge(unittest.TestCase):

    def test_export_includes_hinge_drilling_ops(self):
        from domain.builders import WardrobeBuilder
        from domain.manufacturing_compiler import ManufacturingCompiler
        from domain.rules_engine import HardwarePlacementEngine, RuleContext
        from exports.cnc_exporter import CNCExporter

        cabinet = WardrobeBuilder(
            uid="HINGE_CNC",
            width=1000,
            height=2000,
            depth=600,
        )
        cabinet.add_doors(2)
        project = cabinet.build()

        context = RuleContext()
        HardwarePlacementEngine(context).process(project)

        door_nodes = [
            node for node in project.graph.physical_nodes
            if getattr(node.role, "value", node.role) == "DOOR_PANEL"
        ]
        for placement in project.placements:
            if placement.hardware_intent == "INTENT_HINGE" and door_nodes:
                placement.target_node_id = door_nodes[0].identity.key

        ManufacturingCompiler().compile(project, context)

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "drilling_map.csv")
            CNCExporter.export_master_drilling_map(project, csv_path)

            with open(csv_path, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))

        hinge_rows = [
            row for row in rows
            if float(row["Diameter"]) in (35.0, 2.5)
        ]

        self.assertTrue(any(float(row["Diameter"]) == 35.0 for row in hinge_rows))
        self.assertTrue(any(float(row["Diameter"]) == 2.5 for row in hinge_rows))
        self.assertTrue(any(row["Face"] == "BACK" for row in hinge_rows))
        self.assertTrue(any(float(row["Depth"]) == 12.5 for row in hinge_rows))


if __name__ == "__main__":
    unittest.main()
