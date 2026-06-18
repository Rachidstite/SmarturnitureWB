import csv
import os
import tempfile
import unittest

from domain.builders import WardrobeBuilder
from domain.core_types import NodeCategory, NodeRole
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.rules_engine import RuleContext, ShelfSupportRule
from domain.system32 import System32Engine
from exports.cnc_exporter import CNCExporter
from exports.hardware_report import HardwareReportEngine
from manufacturing.extractor import ManufacturingExtractor


class TestAdjustableShelfRowContract(unittest.TestCase):

    def test_system32_shelf_pin_positions_use_32mm_pitch_and_expected_offsets(self):
        panel_height = 2000.0

        positions = System32Engine.shelf_pin_positions(panel_height)

        self.assertTrue(positions)
        self.assertEqual(positions[0], 64)
        self.assertEqual(positions[-1], 1920)
        self.assertEqual(panel_height - positions[-1], 80.0)
        self.assertTrue(all(pos < panel_height - 64 for pos in positions))
        self.assertTrue(
            all(
                positions[index + 1] - positions[index] == 32.0
                for index in range(len(positions) - 1)
            )
        )

    def test_adjustable_row_holes_do_not_increase_shelf_pin_hardware_quantity(self):
        project, context = self._compiled_project_with_one_shelf()

        report = HardwareReportEngine.generate_from_project(project, context)

        self.assertEqual(report.hardware_items["SHELF_PIN"], 4)

    def test_system32_row_drilling_is_owned_by_physical_side_panels(self):
        project, _context = self._compiled_project_with_one_shelf()
        positions = System32Engine.shelf_pin_positions(2000.0)
        side_panels = project.graph._by_role[NodeRole.SIDE_PANEL]

        row_ops = self._system32_row_ops(side_panels, positions)

        self.assertTrue(side_panels)
        self.assertTrue(
            all(panel.category == NodeCategory.PHYSICAL for panel in side_panels)
        )
        self.assertEqual(
            len(row_ops),
            len(positions) * len(side_panels),
            "System32 row drilling should be machining on physical side panels",
        )

    def test_system32_row_drilling_reaches_extractor_and_cnc_facing_operations(self):
        project, _context = self._compiled_project_with_one_shelf()
        positions = System32Engine.shelf_pin_positions(2000.0)
        side_panels = project.graph._by_role[NodeRole.SIDE_PANEL]
        expected_row_count = len(positions) * len(side_panels)

        specs = ManufacturingExtractor.extract(project.graph)
        extracted_row_ops = [
            op
            for spec in specs
            if spec.identity in {panel.identity.key for panel in side_panels}
            for op in spec.cnc_operations
            if self._matches_system32_row_op(op, positions)
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "drilling_map.csv")
            CNCExporter.export_master_drilling_map(project, csv_path)

            with open(csv_path, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))

        cnc_row_ops = [
            row
            for row in rows
            if row["Panel_ID"] in {panel.identity.key for panel in side_panels}
            and float(row["Diameter"]) == 5.0
            and float(row["Depth"]) == 12.0
            and float(row["Y"]) in positions
        ]

        self.assertEqual(
            len(extracted_row_ops),
            expected_row_count,
            "System32 row drilling should be exposed as machining operations",
        )
        self.assertEqual(
            len(cnc_row_ops),
            expected_row_count,
            "System32 row drilling should appear in CNC-facing output",
        )

    @staticmethod
    def _compiled_project_with_one_shelf():
        cabinet = WardrobeBuilder(
            uid="ADJUSTABLE_SHELF_ROW_CONTRACT",
            width=800.0,
            height=2000.0,
            depth=580.0,
        )
        cabinet.add_shelves(count=1, section_id="ROOT")
        project = cabinet.build()
        context = RuleContext()

        project.placements.extend(ShelfSupportRule().apply(project, context))
        ManufacturingCompiler().compile(project, context)

        return project, context

    @staticmethod
    def _system32_row_ops(side_panels, positions):
        return [
            op
            for panel in side_panels
            for op in getattr(panel, "machining_ops", [])
            if TestAdjustableShelfRowContract._matches_system32_row_op(
                op,
                positions,
            )
        ]

    @staticmethod
    def _matches_system32_row_op(op, positions):
        op_type = getattr(op, "op_type", getattr(op, "operation_type", ""))
        y = getattr(op, "local_y", getattr(op, "y", None))
        return (
            op_type == "DRILL"
            and abs(getattr(op, "diameter", 0.0) - 5.0) < 0.1
            and abs(getattr(op, "depth", 0.0) - 12.0) < 0.1
            and y in positions
        )


if __name__ == "__main__":
    unittest.main()
