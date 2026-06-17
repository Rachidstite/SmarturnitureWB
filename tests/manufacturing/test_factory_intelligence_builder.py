import unittest
from unittest.mock import patch


class TestFactoryIntelligenceBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.factory_intelligence_builder import (
            FactoryIntelligenceBuilder,
        )

        self.assertTrue(callable(FactoryIntelligenceBuilder().build))

    @patch(
        "manufacturing.factory_intelligence_builder.FactoryLoadBuilder"
    )
    @patch(
        "manufacturing.factory_intelligence_builder.FactoryCapacityIntelligenceBuilder"
    )
    @patch(
        "manufacturing.factory_intelligence_builder.FactoryResourceBuilder"
    )
    def test_builder_aggregates_resource_capacity_and_load_reports(
        self,
        resource_builder_class,
        capacity_builder_class,
        load_builder_class,
    ):
        from manufacturing.factory_intelligence_builder import (
            FactoryIntelligenceBuilder,
        )
        from manufacturing.factory_intelligence_report import (
            FactoryIntelligenceReport,
        )

        duration_report = object()
        resource_report = object()
        capacity_report = object()
        load_report = object()

        resource_builder_class.return_value.build.return_value = resource_report
        capacity_builder_class.return_value.build.return_value = capacity_report
        load_builder_class.return_value.build.return_value = load_report

        report = FactoryIntelligenceBuilder().build(duration_report)

        self.assertIsInstance(report, FactoryIntelligenceReport)
        self.assertIs(report.factory_resource_report, resource_report)
        self.assertIs(report.factory_capacity_report, capacity_report)
        self.assertIs(report.factory_load_report, load_report)

        resource_builder_class.return_value.build.assert_called_once_with()
        capacity_builder_class.return_value.build.assert_called_once_with(
            resource_report,
            duration_report,
        )
        load_builder_class.return_value.build.assert_called_once_with(
            resource_report,
            duration_report,
        )

    def test_builder_works_with_real_builders(self):
        from manufacturing.factory_intelligence_builder import (
            FactoryIntelligenceBuilder,
        )
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = FactoryIntelligenceBuilder().build(
            ManufacturingDurationReport(total_production_minutes=480.0)
        )

        self.assertIsNotNone(report.factory_resource_report)
        self.assertIsNotNone(report.factory_capacity_report)
        self.assertIsNotNone(report.factory_load_report)
        self.assertEqual(report.factory_resource_report.workers, 3)
        self.assertEqual(report.factory_capacity_report.required_hours, 8.0)
        self.assertEqual(report.factory_load_report.status, "LOW")


if __name__ == "__main__":
    unittest.main()
