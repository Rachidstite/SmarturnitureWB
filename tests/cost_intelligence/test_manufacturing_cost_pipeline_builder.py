import unittest


class TestManufacturingCostPipelineBuilder(unittest.TestCase):

    def test_manufacturing_cost_pipeline_builder_exists(self):
        from cost_intelligence.manufacturing_cost_pipeline_builder import (
            ManufacturingCostPipelineBuilder,
        )

        self.assertTrue(callable(ManufacturingCostPipelineBuilder().build))

    def test_build_returns_manufacturing_cost_summary(self):
        from cost_intelligence.manufacturing_cost_pipeline_builder import (
            ManufacturingCostPipelineBuilder,
        )
        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )
        from manufacturing.manufacturing_edge_report import ManufacturingEdgeReport
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )
        from manufacturing.manufacturing_summary_report import (
            ManufacturingSummaryReport,
        )

        warnings = ["Missing edge data"]
        production_package = ManufacturingProductionPackage(
            cutlist_report=ManufacturingCutlistReport(
                items=[
                    {
                        "identity": "panel-01",
                        "width": 100.0,
                        "height": 200.0,
                        "thickness": 18.0,
                        "material": "MDF",
                        "quantity": 1,
                    }
                ],
                total_items=1,
                warnings=warnings,
            ),
            edge_report=ManufacturingEdgeReport(
                items=[
                    {
                        "panel_identity": "panel-01",
                        "edge": "TOP",
                        "banding": "ABS_1MM",
                        "linear_meters": 0.1,
                    }
                ],
                total_items=1,
                total_linear_meters=0.1,
                warnings=warnings,
            ),
            machining_report=ManufacturingMachiningReport(
                items=[
                    {
                        "operation_type": "DRILL",
                        "diameter": 5.0,
                        "depth": 12.0,
                        "is_through": False,
                        "x": 100.0,
                        "y": 200.0,
                        "z": 0.0,
                        "face": "TOP",
                        "axis": "Z",
                        "source": "panel-01",
                    }
                ],
                total_items=1,
                warnings=warnings,
            ),
            summary_report=ManufacturingSummaryReport(
                total_panels=1,
                total_materials=1,
                total_edge_operations=1,
                total_machining_operations=1,
                warnings=warnings,
            ),
            warnings=warnings,
        )

        summary = ManufacturingCostPipelineBuilder().build(production_package)

        self.assertIsNotNone(summary.cost_report)
        self.assertIsNotNone(summary.risk_report)
        self.assertIsNotNone(summary.insights)
        self.assertEqual(
            summary.total_manufacturing_cost,
            summary.cost_report.total_manufacturing_cost,
        )
        self.assertEqual(summary.risk_level, summary.risk_report.risk_level)
        self.assertIs(summary.warnings, summary.risk_report.warnings)


if __name__ == "__main__":
    unittest.main()
