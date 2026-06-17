import csv
import os
import tempfile
import unittest


class TestCNCExportMinifix(unittest.TestCase):

    def test_export_includes_minifix_drilling_ops(self):
        from domain.builders import WardrobeBuilder
        from domain.core_types import JoineryType
        from domain.manufacturing_compiler import ManufacturingCompiler
        from domain.rules_engine import HardwarePlacementEngine, RuleContext
        from exports.cnc_exporter import CNCExporter

        project = WardrobeBuilder(
            uid="MINIFIX_CNC",
            width=1000,
            height=2000,
            depth=600,
        ).build()

        context = RuleContext(preferred_connector=JoineryType.MINIFIX_15)
        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "drilling_map.csv")
            CNCExporter.export_master_drilling_map(project, csv_path)

            with open(csv_path, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))

        minifix_rows = [
            row
            for row in rows
            if float(row["Diameter"]) in (15.0, 8.0)
        ]

        self.assertTrue(any(float(row["Diameter"]) == 15.0 for row in minifix_rows))
        self.assertTrue(any(float(row["Diameter"]) == 8.0 for row in minifix_rows))
        self.assertTrue(
            any(row["Face"] in ("FRONT", "LEFT", "RIGHT", "BACK") for row in minifix_rows)
        )
        self.assertTrue(
            any(row["Axis"] == "X" for row in minifix_rows if float(row["Diameter"]) == 8.0)
        )


if __name__ == "__main__":
    unittest.main()
