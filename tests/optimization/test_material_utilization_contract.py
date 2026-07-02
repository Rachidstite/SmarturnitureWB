import importlib
import inspect
import unittest
from types import SimpleNamespace


class TestMaterialUtilizationContract(unittest.TestCase):
    def test_manufacturing_metrics_produce_material_utilization_inputs(self):
        from manufacturing.manufacturing_metrics_builder import (
            ManufacturingMetricsBuilder,
        )

        production_package = SimpleNamespace(
            cutlist_report=SimpleNamespace(
                items=[
                    {
                        "width": 500.0,
                        "height": 700.0,
                        "quantity": 2,
                        "material": "MDF_18",
                    }
                ]
            ),
            edge_report=SimpleNamespace(
                items=[
                    {"banding": "PVC_1", "linear_meters": 6.0},
                ],
                total_linear_meters=6.0,
            ),
            machining_report=SimpleNamespace(
                items=[
                    {"operation_type": "DRILL"},
                    {"operation_type": "DRILL"},
                    {"operation_type": "GROOVE"},
                ]
            ),
            summary_report=SimpleNamespace(total_panels=2),
            warnings=[],
        )

        report = ManufacturingMetricsBuilder().build(production_package)

        self.assertEqual(report.total_panels, 2)
        self.assertGreater(report.total_panel_area_m2, 0.0)
        self.assertEqual(report.total_drilling_operations, 2)
        self.assertEqual(report.total_material_types, 1)

    def test_sheet_utilization_must_influence_waste_estimation(self):
        source = inspect.getsource(
            importlib.import_module("cost_intelligence.waste_intelligence_builder")
        )

        self.assertRegex(
            source,
            r"sheet_utilization|utilization_rate|waste_rate",
        )

    def test_material_optimization_pipeline_already_consumes_sheet_utilization(self):
        source = inspect.getsource(
            importlib.import_module(
                "cost_intelligence.manufacturing_optimization_pipeline_builder"
            )
        )

        self.assertIn("SheetUtilizationBuilder().build", source)
        self.assertIn("sheet_utilization_report", source)


if __name__ == "__main__":
    unittest.main()
