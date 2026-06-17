import unittest
from dataclasses import fields, is_dataclass


class TestFactoryBottleneckIntelligenceReportContract(unittest.TestCase):

    def test_report_is_dataclass_with_exact_field_order(self):
        from manufacturing.factory_bottleneck_intelligence_report import (
            FactoryBottleneckIntelligenceReport,
        )

        self.assertTrue(is_dataclass(FactoryBottleneckIntelligenceReport))
        self.assertEqual(
            [field.name for field in fields(FactoryBottleneckIntelligenceReport)],
            [
                "bottleneck",
                "load_percent",
                "severity",
                "impact",
                "recommendation",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.factory_bottleneck_intelligence_report import (
            FactoryBottleneckIntelligenceReport,
        )

        report = FactoryBottleneckIntelligenceReport()

        self.assertEqual(report.bottleneck, "")
        self.assertEqual(report.load_percent, 0.0)
        self.assertEqual(report.severity, "LOW")
        self.assertEqual(report.impact, "NO_MAJOR_BOTTLENECK")
        self.assertEqual(report.recommendation, "No bottleneck detected")


if __name__ == "__main__":
    unittest.main()
