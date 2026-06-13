import unittest
from dataclasses import fields, is_dataclass
from unittest.mock import patch


class TestManufacturingFactoryIntelligencePipelineBuilder(unittest.TestCase):

    def test_factory_result_is_dataclass_with_exact_field_order(self):
        from cost_intelligence.manufacturing_factory_intelligence_result import (
            ManufacturingFactoryIntelligenceResult,
        )

        self.assertTrue(is_dataclass(ManufacturingFactoryIntelligenceResult))
        self.assertEqual(
            [
                field.name
                for field in fields(ManufacturingFactoryIntelligenceResult)
            ],
            [
                "manufacturing_cost_summary",
                "manufacturing_optimization_result",
                "manufacturing_commercial_result",
                "production_readiness_report",
                "manufacturing_kpi_report",
                "manufacturing_executive_report",
            ],
        )

    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingExecutiveReportBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingKPIBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ProductionReadinessBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingCommercialPipelineBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingOptimizationPipelineBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingCostPipelineBuilder"
    )
    def test_pipeline_orchestrates_builders_in_order_and_returns_results(
        self,
        cost_builder_class,
        optimization_builder_class,
        commercial_builder_class,
        readiness_builder_class,
        kpi_builder_class,
        executive_builder_class,
    ):
        from cost_intelligence.manufacturing_factory_intelligence_pipeline_builder import (
            ManufacturingFactoryIntelligencePipelineBuilder,
        )
        from cost_intelligence.manufacturing_factory_intelligence_result import (
            ManufacturingFactoryIntelligenceResult,
        )

        production_package = object()
        cost_summary = object()
        optimization_result = object()
        commercial_result = object()
        readiness_report = object()
        kpi_report = object()
        executive_report = object()
        calls = []

        builders = [
            (cost_builder_class, "cost", cost_summary),
            (optimization_builder_class, "optimization", optimization_result),
            (commercial_builder_class, "commercial", commercial_result),
            (readiness_builder_class, "readiness", readiness_report),
            (kpi_builder_class, "kpi", kpi_report),
            (executive_builder_class, "executive", executive_report),
        ]
        for builder_class, name, result in builders:
            builder_class.return_value.build.side_effect = (
                lambda *args, _name=name, _result=result, **kwargs: (
                    calls.append(_name),
                    _result,
                )[1]
            )

        result = ManufacturingFactoryIntelligencePipelineBuilder().build(
            production_package,
            markup_rate=0.25,
            currency="EUR",
        )

        self.assertEqual(
            calls,
            [
                "cost",
                "optimization",
                "commercial",
                "readiness",
                "kpi",
                "executive",
            ],
        )
        self.assertIsInstance(result, ManufacturingFactoryIntelligenceResult)
        self.assertIs(result.manufacturing_cost_summary, cost_summary)
        self.assertIs(result.manufacturing_optimization_result, optimization_result)
        self.assertIs(result.manufacturing_commercial_result, commercial_result)
        self.assertIs(result.production_readiness_report, readiness_report)
        self.assertIs(result.manufacturing_kpi_report, kpi_report)
        self.assertIs(result.manufacturing_executive_report, executive_report)

        cost_builder_class.return_value.build.assert_called_once_with(
            production_package
        )
        optimization_builder_class.return_value.build.assert_called_once_with(
            production_package
        )
        commercial_builder_class.return_value.build.assert_called_once_with(
            production_package,
            0.25,
            "EUR",
        )
        readiness_builder_class.return_value.build.assert_called_once_with(
            production_package,
            cost_summary,
            optimization_result,
            commercial_result,
        )
        kpi_builder_class.return_value.build.assert_called_once_with(
            cost_summary,
            optimization_result,
            commercial_result,
            readiness_report,
        )
        executive_builder_class.return_value.build.assert_called_once_with(
            kpi_report,
            readiness_report,
            optimization_result,
        )

    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingExecutiveReportBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingKPIBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ProductionReadinessBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingCommercialPipelineBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingOptimizationPipelineBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingCostPipelineBuilder"
    )
    def test_pipeline_uses_defaults_and_does_not_mutate_package(
        self,
        cost_builder_class,
        optimization_builder_class,
        commercial_builder_class,
        readiness_builder_class,
        kpi_builder_class,
        executive_builder_class,
    ):
        from cost_intelligence.manufacturing_factory_intelligence_pipeline_builder import (
            ManufacturingFactoryIntelligencePipelineBuilder,
        )
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        warnings = ["Package warning"]
        production_package = ManufacturingProductionPackage(
            release_ready=True,
            warnings=warnings,
        )

        ManufacturingFactoryIntelligencePipelineBuilder().build(
            production_package
        )

        commercial_builder_class.return_value.build.assert_called_once_with(
            production_package,
            0.0,
            "MAD",
        )
        self.assertTrue(production_package.release_ready)
        self.assertIs(production_package.warnings, warnings)
        self.assertEqual(production_package.warnings, ["Package warning"])


if __name__ == "__main__":
    unittest.main()
