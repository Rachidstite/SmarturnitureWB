import unittest
from types import SimpleNamespace
from unittest.mock import patch


class TestFurnitureProjectFactoryDecisionBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.furniture_project_factory_decision_builder import (
            FurnitureProjectFactoryDecisionBuilder,
        )

        self.assertTrue(callable(FurnitureProjectFactoryDecisionBuilder().build))

    @patch(
        "cost_intelligence.furniture_project_factory_decision_builder."
        "FactoryDecisionBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_factory_decision_builder."
        "ManufacturingFactoryIntelligencePipelineBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_factory_decision_builder."
        "ManufacturingProductionPackageBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_factory_decision_builder."
        "FurnitureProjectManufacturingPackageBuilder"
    )
    def test_builder_delegates_to_existing_components_and_returns_decision(
        self,
        project_package_builder_class,
        production_package_builder_class,
        factory_pipeline_builder_class,
        decision_builder_class,
    ):
        from cost_intelligence.furniture_project_factory_decision_builder import (
            FurnitureProjectFactoryDecisionBuilder,
        )

        furniture_project = object()
        manufacturing_package = object()
        production_package = object()
        readiness_report = object()
        cost_summary = object()
        waste_report = object()
        nesting_report = object()
        quotation_intelligence_report = object()
        factory_result = SimpleNamespace(
            production_readiness_report=readiness_report,
            manufacturing_cost_summary=cost_summary,
            manufacturing_optimization_result=SimpleNamespace(
                waste_intelligence_report=waste_report,
                nesting_intelligence_report=nesting_report,
            ),
            manufacturing_commercial_result=SimpleNamespace(
                quotation_intelligence_report=quotation_intelligence_report,
            ),
        )
        expected_decision = object()
        project_package_builder_class.return_value.build.return_value = (
            manufacturing_package
        )
        production_package_builder_class.return_value.build.return_value = (
            production_package
        )
        factory_pipeline_builder_class.return_value.build.return_value = (
            factory_result
        )
        decision_builder_class.return_value.build.return_value = expected_decision

        result = FurnitureProjectFactoryDecisionBuilder().build(
            furniture_project,
            markup_rate=0.25,
            currency="EUR",
        )

        project_package_builder_class.return_value.build.assert_called_once_with(
            furniture_project
        )
        production_package_builder_class.return_value.build.assert_called_once_with(
            manufacturing_package
        )
        factory_pipeline_builder_class.return_value.build.assert_called_once_with(
            production_package,
            0.25,
            "EUR",
        )
        decision_builder_class.return_value.build.assert_called_once_with(
            readiness_report,
            cost_summary,
            waste_report,
            nesting_report,
            quotation_intelligence_report,
        )
        self.assertIs(result, expected_decision)

    @patch(
        "cost_intelligence.furniture_project_factory_decision_builder."
        "FactoryDecisionBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_factory_decision_builder."
        "ManufacturingFactoryIntelligencePipelineBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_factory_decision_builder."
        "ManufacturingProductionPackageBuilder"
    )
    @patch(
        "cost_intelligence.furniture_project_factory_decision_builder."
        "FurnitureProjectManufacturingPackageBuilder"
    )
    def test_builder_uses_defaults_and_does_not_mutate_furniture_project(
        self,
        project_package_builder_class,
        production_package_builder_class,
        factory_pipeline_builder_class,
        decision_builder_class,
    ):
        from cost_intelligence.furniture_project_factory_decision_builder import (
            FurnitureProjectFactoryDecisionBuilder,
        )
        from domain.furniture_project import FurnitureProject

        cabinets = [object()]
        metadata = {"customer": "Example"}
        furniture_project = FurnitureProject(
            project_id="PROJECT-1",
            name="Kitchen",
            cabinets=cabinets,
            metadata=metadata,
        )
        original_values = furniture_project.__dict__.copy()
        manufacturing_package = object()
        production_package = object()
        factory_result = SimpleNamespace(
            production_readiness_report=object(),
            manufacturing_cost_summary=object(),
            manufacturing_optimization_result=SimpleNamespace(
                waste_intelligence_report=object(),
                nesting_intelligence_report=object(),
            ),
            manufacturing_commercial_result=SimpleNamespace(
                quotation_intelligence_report=object(),
            ),
        )
        project_package_builder_class.return_value.build.return_value = (
            manufacturing_package
        )
        production_package_builder_class.return_value.build.return_value = (
            production_package
        )
        factory_pipeline_builder_class.return_value.build.return_value = factory_result

        FurnitureProjectFactoryDecisionBuilder().build(furniture_project)

        factory_pipeline_builder_class.return_value.build.assert_called_once_with(
            production_package,
            0.0,
            "MAD",
        )
        self.assertEqual(furniture_project.__dict__, original_values)
        self.assertIs(furniture_project.cabinets, cabinets)
        self.assertIs(furniture_project.metadata, metadata)


if __name__ == "__main__":
    unittest.main()
