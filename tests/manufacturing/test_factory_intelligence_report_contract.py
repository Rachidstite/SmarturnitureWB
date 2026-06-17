import unittest
from dataclasses import fields, is_dataclass


class TestFactoryIntelligenceReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.factory_intelligence_report import (
            FactoryIntelligenceReport,
        )

        self.assertTrue(is_dataclass(FactoryIntelligenceReport))

    def test_report_has_required_fields_in_order(self):
        from manufacturing.factory_intelligence_report import (
            FactoryIntelligenceReport,
        )

        self.assertEqual(
            [field.name for field in fields(FactoryIntelligenceReport)],
            [
                "factory_resource_report",
                "factory_capacity_report",
                "factory_load_report",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.factory_intelligence_report import (
            FactoryIntelligenceReport,
        )

        report = FactoryIntelligenceReport()

        self.assertIsNone(report.factory_resource_report)
        self.assertIsNone(report.factory_capacity_report)
        self.assertIsNone(report.factory_load_report)


if __name__ == "__main__":
    unittest.main()
