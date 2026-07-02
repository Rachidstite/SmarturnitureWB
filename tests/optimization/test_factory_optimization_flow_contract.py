import importlib
import inspect
import unittest


class TestFactoryOptimizationFlowContract(unittest.TestCase):
    def test_manufacturing_optimization_pipeline_is_existing_aggregation_seam(self):
        from cost_intelligence.manufacturing_optimization_pipeline_builder import (
            ManufacturingOptimizationPipelineBuilder,
        )

        source = inspect.getsource(
            importlib.import_module(
                "cost_intelligence.manufacturing_optimization_pipeline_builder"
            )
        )

        self.assertIn("ManufacturingOptimizationPipelineBuilder", source)
        self.assertIn("SheetUtilizationBuilder", source)
        self.assertIn("OffcutExtractionService", source)
        self.assertIn("OffcutIntelligenceBuilder", source)
        self.assertIn("WasteIntelligenceBuilder", source)
        self.assertIn("NestingIntelligenceBuilder", source)
        self.assertNotIn("OptimizationEngine", source)
        self.assertNotIn("FactoryOptimizationEngine", source)
        self.assertTrue(inspect.isclass(ManufacturingOptimizationPipelineBuilder))

    def test_pipeline_returns_existing_optimization_result_contract(self):
        from cost_intelligence.manufacturing_optimization_result import (
            ManufacturingOptimizationResult,
        )

        field_names = tuple(ManufacturingOptimizationResult.__dataclass_fields__)
        self.assertEqual(
            field_names,
            (
                "sheet_utilization_report",
                "offcut_report",
                "offcut_intelligence_report",
                "waste_intelligence_report",
                "nesting_intelligence_report",
            ),
        )

    def test_pipeline_reuses_existing_optimization_builders_only_once(self):
        source = inspect.getsource(
            importlib.import_module(
                "cost_intelligence.manufacturing_optimization_pipeline_builder"
            )
        )

        for builder_name in (
            "SheetUtilizationBuilder",
            "OffcutIntelligenceBuilder",
            "WasteIntelligenceBuilder",
            "NestingIntelligenceBuilder",
        ):
            with self.subTest(builder_name=builder_name):
                self.assertEqual(source.count(builder_name), 2)


if __name__ == "__main__":
    unittest.main()
