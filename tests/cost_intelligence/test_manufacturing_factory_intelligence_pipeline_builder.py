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
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingMetricsBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingDurationBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingCapacityBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ProductionScheduleBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "FactoryWorkloadBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingComplexityBuilder"
    )
    def test_pipeline_orchestrates_builders_in_order_and_returns_results(
        self,
        complexity_builder_class,
        workload_builder_class,
        schedule_builder_class,
        capacity_builder_class,
        duration_builder_class,
        metrics_builder_class,
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
        metrics_report = object()
        duration_report = object()
        capacity_report = object()
        schedule_report = object()
        workload_report = object()
        complexity_report = object()
        executive_report = object()
        calls = []

        builders = [
            (metrics_builder_class, "metrics", metrics_report),
            (duration_builder_class, "duration", duration_report),
            (capacity_builder_class, "capacity", capacity_report),
            (schedule_builder_class, "schedule", schedule_report),
            (workload_builder_class, "workload", workload_report),
            (complexity_builder_class, "complexity", complexity_report),
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
                "metrics",
                "duration",
                "capacity",
                "schedule",
                "workload",
                "complexity",
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
        optimization_builder_class.return_value.build.assert_called_once()
        optimization_args, optimization_kwargs = (
            optimization_builder_class.return_value.build.call_args
        )
        self.assertEqual(optimization_args[0], [])
        self.assertEqual(optimization_args[1].waste_ratio, 0.0)
        self.assertEqual(optimization_args[2].waste_cost, 0.0)
        self.assertEqual(optimization_kwargs, {})
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
        metrics_builder_class.return_value.build.assert_called_once_with(
            production_package
        )
        duration_builder_class.return_value.build.assert_called_once_with(
            metrics_report
        )
        capacity_builder_class.return_value.build.assert_called_once_with(
            duration_report
        )
        schedule_builder_class.return_value.build.assert_called_once_with(
            duration_report,
            capacity_report,
        )
        workload_builder_class.return_value.build.assert_called_once_with(
            [schedule_report]
        )
        complexity_builder_class.return_value.build.assert_called_once_with(
            metrics_report
        )
        executive_builder_class.return_value.build.assert_called_once_with(
            kpi_report,
            readiness_report,
            optimization_result,
            capacity_report=capacity_report,
            production_schedule_report=schedule_report,
            factory_workload_report=workload_report,
            manufacturing_complexity_report=complexity_report,
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
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingMetricsBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingDurationBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingCapacityBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ProductionScheduleBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "FactoryWorkloadBuilder"
    )
    @patch(
        "cost_intelligence.manufacturing_factory_intelligence_pipeline_builder."
        "ManufacturingComplexityBuilder"
    )
    def test_pipeline_uses_defaults_and_does_not_mutate_package(
        self,
        complexity_builder_class,
        workload_builder_class,
        schedule_builder_class,
        capacity_builder_class,
        duration_builder_class,
        metrics_builder_class,
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

        metrics_builder_class.return_value.build.return_value = object()
        duration_builder_class.return_value.build.return_value = object()
        capacity_builder_class.return_value.build.return_value = object()
        schedule_builder_class.return_value.build.return_value = object()
        workload_builder_class.return_value.build.return_value = object()
        complexity_builder_class.return_value.build.return_value = object()

        ManufacturingFactoryIntelligencePipelineBuilder().build(
            production_package
        )

        commercial_builder_class.return_value.build.assert_called_once_with(
            production_package,
            0.0,
            "MAD",
        )
        optimization_builder_class.return_value.build.assert_called_once()
        optimization_args, optimization_kwargs = (
            optimization_builder_class.return_value.build.call_args
        )
        self.assertEqual(optimization_args[0], [])
        self.assertEqual(optimization_args[1].waste_ratio, 0.0)
        self.assertEqual(optimization_args[2].waste_cost, 0.0)
        self.assertEqual(optimization_kwargs, {})
        self.assertTrue(production_package.release_ready)
        self.assertIs(production_package.warnings, warnings)
        self.assertEqual(production_package.warnings, ["Package warning"])


if __name__ == "__main__":
    unittest.main()
