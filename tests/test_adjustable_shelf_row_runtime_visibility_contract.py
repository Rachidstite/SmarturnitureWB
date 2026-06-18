import unittest

from cost_intelligence.hardware_report_cost_service import HardwareReportCostService
from domain.builders import WardrobeBuilder
from domain.core_types import NodeCategory, NodeRole
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.rules_engine import RuleContext, ShelfSupportRule
from domain.system32 import System32Engine
from exports.hardware_report import HardwareReportEngine
from manufacturing.extractor import ManufacturingExtractor
from manufacturing.manufacturing_metrics_builder import ManufacturingMetricsBuilder
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)


class TestAdjustableShelfRowRuntimeVisibilityContract(unittest.TestCase):

    def test_system32_row_operations_exist_on_physical_side_panels(self):
        project, _context = self._compiled_project_with_one_shelf()
        positions = System32Engine.shelf_pin_positions(2000.0)
        side_panels = project.graph._by_role[NodeRole.SIDE_PANEL]

        row_ops = self._row_node_ops(side_panels, positions)

        self.assertTrue(side_panels)
        self.assertTrue(
            all(panel.category == NodeCategory.PHYSICAL for panel in side_panels)
        )
        self.assertEqual(
            len(row_ops),
            len(positions) * len(side_panels),
            "System32 shelf rows should be machining on physical side panels",
        )

    def test_system32_row_operations_are_visible_in_extractor_and_runtime(self):
        project, _context = self._compiled_project_with_one_shelf()
        positions = System32Engine.shelf_pin_positions(2000.0)
        side_panel_ids = {
            panel.identity.key
            for panel in project.graph._by_role[NodeRole.SIDE_PANEL]
        }
        expected_row_count = len(positions) * len(side_panel_ids)

        specs = ManufacturingExtractor.extract(project.graph)
        extracted_row_ops = [
            op
            for spec in specs
            if spec.identity in side_panel_ids
            for op in spec.cnc_operations
            if self._matches_row_operation(op, positions)
        ]

        runtime = ManufacturingRuntimePipelineBuilder().build(project.graph)
        runtime_row_ops = [
            op
            for op in runtime.manufacturing_package.machining_operations
            if self._matches_row_operation(op, positions)
        ]
        metrics = ManufacturingMetricsBuilder().build(
            runtime.manufacturing_production_package
        )

        self.assertEqual(
            len(extracted_row_ops),
            expected_row_count,
            "ManufacturingExtractor should expose System32 row machining",
        )
        self.assertEqual(
            len(runtime_row_ops),
            expected_row_count,
            "ManufacturingRuntimePipelineBuilder should preserve row machining",
        )
        self.assertGreaterEqual(
            metrics.total_drilling_operations,
            expected_row_count,
            "System32 rows should increase drilling operation count",
        )
        self.assertGreaterEqual(
            runtime.manufacturing_production_package.machining_report.total_items,
            expected_row_count,
            "System32 rows should increase machining report totals",
        )

    def test_system32_row_operations_do_not_increase_shelf_pin_hardware_cost(self):
        project, context = self._compiled_project_with_one_shelf()

        report = HardwareReportEngine.generate_from_project(project, context)
        cost = HardwareReportCostService.estimate_from_project(
            project,
            context,
            pricing_catalog={"SHELF_PIN_5MM": {"unit_price": 2.0}},
        )

        self.assertEqual(report.hardware_items["SHELF_PIN"], 4)
        self.assertEqual(cost.hardware_cost, 8.0)

    @staticmethod
    def _compiled_project_with_one_shelf():
        cabinet = WardrobeBuilder(
            uid="ADJUSTABLE_SHELF_ROW_RUNTIME_CONTRACT",
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
    def _row_node_ops(side_panels, positions):
        return [
            op
            for panel in side_panels
            for op in getattr(panel, "machining_ops", [])
            if TestAdjustableShelfRowRuntimeVisibilityContract._matches_row_operation(
                op,
                positions,
            )
        ]

    @staticmethod
    def _matches_row_operation(op, positions):
        operation_type = getattr(op, "op_type", getattr(op, "operation_type", ""))
        y = getattr(op, "local_y", getattr(op, "y", None))
        return (
            operation_type == "DRILL"
            and abs(getattr(op, "diameter", 0.0) - 5.0) < 0.1
            and abs(getattr(op, "depth", 0.0) - 12.0) < 0.1
            and y in positions
        )


if __name__ == "__main__":
    unittest.main()
